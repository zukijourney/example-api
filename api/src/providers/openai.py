import ujson
import time
import httpx
from dataclasses import dataclass
from fastapi import Request, Response, UploadFile
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Tuple, AsyncGenerator, Union
from ..models import EmbeddingsInput
from ..responses import JSONResponse, StreamingResponseWithStatusCode
from ..core import settings, user_manager, provider_manager
from ..utils import request_processor
from .base_provider import BaseProvider, ProviderConfig
from .utils import WebhookManager, ResponseGenerator, ErrorHandler

@dataclass
class OpenAIConfig:
    api_base_url: str = 'https://api.openai.com/v1'
    provider_id: str = 'oai'
    timeout: int = 100

class OpenAI(BaseProvider):
    config = ProviderConfig(
        name='OpenAI',
        supports_vision=True,
        supports_tool_calling=True,
        supports_real_streaming=True,
        free_models=[
            'gpt-3.5-turbo',
            'gpt-4o',
            'gpt-4o-mini',
            'tts-1',
            'text-embedding-3-small',
            'text-embedding-3-large',
            'omni-moderation-latest',
            'whisper-1'
        ],
        paid_models=[
            'gpt-4',
            'gpt-4-turbo-preview',
            'gpt-4-turbo',
            'chatgpt-4o-latest',
            'o1-mini',
            'o1-preview',
            'dall-e-3',
            'tts-1-hd'
        ],
        model_prices={}
    )

    def __init__(self):
        super().__init__()
        self.sub_providers_db = AsyncIOMotorClient(settings.db_url)['db']['sub_providers']
        self.api_config = OpenAIConfig()

    async def _get_sub_provider(self, model: str) -> Dict[str, Any]:
        sub_providers = await self.sub_providers_db.find({
            'main_provider': self.config.name,
            'models.api_name': {'$in': [model]}
        }).to_list(length=None)
        return min(sub_providers, key=lambda x: (x.get('usage', 0), x.get('last_used', 0)))

    async def _update_sub_provider(self, api_key: str, new_data: Dict[str, Any]) -> None:
        await self.sub_providers_db.find_one_and_update(
            filter={'api_key': api_key},
            update={'$set': new_data},
            upsert=True
        )

    async def _disable_sub_provider(self, api_key: str) -> None:
        await self.sub_providers_db.delete_one(filter={'api_key': api_key})

    def _generate_error_response(self, message: str = 'Something went wrong. Try again later.') -> JSONResponse:
        return JSONResponse(
            content={
                'error': {
                    'message': message,
                    'provider_id': self.api_config.provider_id,
                    'type': 'invalid_response_error',
                    'code': 500
                }
            },
            status_code=500
        )

    async def _handle_error(self, request: Request, model: str, status_code: int) -> None:
        await WebhookManager.send_to_webhook(
            request=request,
            is_error=True,
            model=model,
            pid=self.api_config.provider_id,
            exception=f'Status Code: {status_code}'
        )
        request.state.provider['failures'] += 1
        await provider_manager.update_provider(self.config.name, request.state.provider)

    @classmethod
    @ErrorHandler.retry_provider(max_retries=3)
    async def chat_completions(
        cls,
        request: Request,
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool,
        **kwargs
    ) -> Union[JSONResponse, StreamingResponseWithStatusCode]:
        instance = cls()

        sub_provider = await instance._get_sub_provider(model)
        model = next((m['provider_name'] for m in sub_provider['models'] if m['api_name'] == model), None)
        start = time.time()

        try:
            request.state.user['credits'] -= request.state.token_count
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            if not stream:
                return await instance._handle_non_streaming_chat(
                    request=request,
                    model=model,
                    messages=messages,
                    sub_provider=sub_provider,
                    start=start,
                    **kwargs
                )
            return await instance._handle_streaming_chat(
                request=request,
                model=model,
                messages=messages,
                sub_provider=sub_provider,
                start=start,
                **kwargs
            )
        except httpx.HTTPError as e:
            await WebhookManager.send_to_webhook(request, True, model, instance.api_config.provider_id, str(e))
            await instance._handle_error(request, model, 500)
            return instance._generate_error_response()

    @classmethod
    async def images_generations(
        cls,
        request: Request,
        model: str,
        prompt: str,
        **kwargs
    ) -> JSONResponse:
        instance = cls()

        if 'negative_prompt' in kwargs:
            del kwargs['negative_prompt']

        async with httpx.AsyncClient() as client:
            sub_provider = await instance._get_sub_provider(model)
            response = await client.post(
                url=f'{instance.api_config.api_base_url}/images/generations',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                json={'model': model, 'prompt': prompt, **kwargs},
                timeout=10000
            )

            if response.status_code >= 400:
                if response.status_code in [401, 403, 429]:
                    await instance._disable_sub_provider(sub_provider['api_key'])
                await instance._handle_error(request, model, response.status_code)
                return instance._generate_error_response()

            token_count = instance.config.model_prices.get(model, 10)
            request.state.user['credits'] -= token_count
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            return JSONResponse({
                'provider_id': instance.api_config.provider_id,
                **response.json()
            })

    @classmethod
    async def embeddings(
        cls,
        request: Request,
        model: str,
        input: EmbeddingsInput,
        **kwargs
    ) -> JSONResponse:
        instance = cls()

        async with httpx.AsyncClient() as client:
            sub_provider = await instance._get_sub_provider(model)
            response = await client.post(
                url=f'{instance.api_config.api_base_url}/embeddings',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                json={'model': model, 'input': input, **kwargs}
            )

            if response.status_code >= 400:
                if response.status_code in [401, 403, 429]:
                    await instance._disable_sub_provider(sub_provider['api_key'])
                await instance._handle_error(request, model, response.status_code)
                return instance._generate_error_response()

            request.state.user['credits'] -= 100
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            return JSONResponse({
                'provider_id': instance.api_config.provider_id,
                **response.json()
            })

    @classmethod
    async def moderations(
        cls,
        request: Request,
        model: str,
        input: Union[str, List[str]]
    ) -> JSONResponse:
        instance = cls()

        async with httpx.AsyncClient() as client:
            sub_provider = await instance._get_sub_provider(model)
            response = await client.post(
                url=f'{instance.api_config.api_base_url}/moderations',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                json={'model': model, 'input': input}
            )

            if response.status_code >= 400:
                if response.status_code in [401, 403, 429]:
                    await instance._disable_sub_provider(sub_provider['api_key'])
                await instance._handle_error(request, model, response.status_code)
                return instance._generate_error_response()

            request.state.user['credits'] -= 10
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            return JSONResponse({
                'provider_id': instance.api_config.provider_id,
                **response.json()
            })

    @classmethod
    async def audio_speech(
        cls,
        request: Request,
        model: str,
        input: str,
        **kwargs
    ) -> Response:
        instance = cls()

        async with httpx.AsyncClient() as client:
            sub_provider = await instance._get_sub_provider(model)
            response = await client.post(
                url=f'{instance.api_config.api_base_url}/audio/speech',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                json={'model': model, 'input': input, **kwargs}
            )

            if response.status_code >= 400:
                if response.status_code in [401, 403, 429]:
                    await instance._disable_sub_provider(sub_provider['api_key'])
                await instance._handle_error(request, model, response.status_code)
                return instance._generate_error_response()

            request.state.user['credits'] -= instance.config.model_prices.get(model, 10)
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            return Response(
                content=response.content,
                media_type='audio/mpeg',
                headers={'Content-Disposition': 'attachment;filename=audio.mp3'}
            )
    
    @classmethod
    async def audio_transcriptions(
        cls,
        request: Request,
        model: str,
        file: UploadFile
    ) -> JSONResponse:
        instance = cls()

        async with httpx.AsyncClient() as client:
            sub_provider = await instance._get_sub_provider(model)
            response = await client.post(
                url=f'{instance.api_config.api_base_url}/audio/transcriptions',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                files={'model': (None, model), 'file': (file.filename, file.file)}
            )

            if response.is_error:
                if response.status_code in [401, 403, 429]:
                    await instance._disable_sub_provider(sub_provider['api_key'])
                await instance._handle_error(request, model, response.status_code)
                return instance._generate_error_response()

            request.state.user['credits'] -= 100
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            return JSONResponse({
                'provider_id': instance.api_config.provider_id,
                **response.json()
            })
    
    @classmethod
    async def audio_translations(
        cls,
        request: Request,
        model: str,
        file: UploadFile
    ) -> JSONResponse:
        instance = cls()

        async with httpx.AsyncClient() as client:
            sub_provider = await instance._get_sub_provider(model)
            response = await client.post(
                url=f'{instance.api_config.api_base_url}/audio/translations',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                files={'model': (None, model), 'file': (file.filename, file.file)}
            )

            if response.status_code >= 400:
                if response.status_code in [401, 403, 429]:
                    await instance._disable_sub_provider(sub_provider['api_key'])
                await instance._handle_error(request, model, response.status_code)
                return instance._generate_error_response()

            request.state.user['credits'] -= 100
            await user_manager.update_user(request.state.user['user_id'], request.state.user)

            return JSONResponse({
                'provider_id': instance.api_config.provider_id,
                **response.json()
            })

    async def _handle_non_streaming_chat(
        self,
        request: Request,
        model: str,
        messages: List[Dict[str, Any]],
        sub_provider: Dict[str, Any],
        start: float,
        **kwargs
    ) -> JSONResponse:
        async with httpx.AsyncClient(verify=False, timeout=self.api_config.timeout) as client:
            response = await client.post(
                url=f'{self.api_config.api_base_url}/chat/completions',
                headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                json={
                    'model': model,
                    'messages': messages,
                    'stream': False,
                    **kwargs
                }
            )
            
            if response.status_code >= 400:
                if response.status_code in [401, 403, 429]:
                    await self._disable_sub_provider(sub_provider['api_key'])
                await self._handle_error(request, model, response.status_code)
                return self._generate_error_response()

            await self._update_metrics(request, sub_provider, response, start)
            return JSONResponse({
                'provider_id': self.api_config.provider_id,
                **response.json()
            })

    async def _handle_streaming_chat(
        self,
        request: Request,
        model: str,
        messages: List[Dict[str, Any]],
        sub_provider: Dict[str, Any],
        start: float,
        **kwargs
    ) -> StreamingResponseWithStatusCode:
        async def stream_response() -> AsyncGenerator[Tuple[str, int], None]:
            success = True
            try:
                async with httpx.AsyncClient(verify=False, timeout=self.api_config.timeout) as client:
                    async with client.stream(
                        method='POST',
                        url=f'{self.api_config.api_base_url}/chat/completions',
                        headers={'Authorization': f'Bearer {sub_provider["api_key"]}'},
                        json={
                            'model': model,
                            'messages': messages,
                            'stream': True,
                            **kwargs
                        }
                    ) as response:
                        if response.status_code >= 400:
                            if response.status_code in [401, 403, 429]:
                                await self._disable_sub_provider(sub_provider['api_key'])
                            success = False
                            await self._handle_error(request, model, response.status_code)
                            yield ResponseGenerator.generate_error('An error occurred. Try again later.', self.api_config.provider_id), 500
                        else:
                            await self._update_streaming_metrics(request, sub_provider, start)
                            
                            async for line in response.aiter_lines():
                                if line.startswith('data: ') and not line.startswith('data: [DONE]'):
                                    yield await self._process_stream_chunk(request, line)

                        if success:
                            yield 'data: [DONE]\n\n', 200
            except httpx.HTTPError:
                await self._handle_error(request, model, 500)
                yield ResponseGenerator.generate_error('Stream interrupted', self.api_config.provider_id), 500

        return StreamingResponseWithStatusCode(
            content=stream_response(),
            media_type='text/event-stream'
        )

    async def _update_metrics(
        self,
        request: Request,
        sub_provider: Dict[str, Any],
        response: httpx.Response,
        start: float
    ) -> None:
        elapsed = time.time() - start
        json_response = response.json()
        
        word_count = sum(
            len(choice['message']['content'])
            for choice in json_response['choices']
            if choice['message']['content']
        )
        token_count = sum(
            request_processor.count_tokens(choice['message']['content'])
            for choice in json_response['choices']
            if choice['message']['content']
        )

        latency_avg = (elapsed / word_count) if elapsed > 0 else 0

        request.state.provider['usage'] += 1
        request.state.provider['latency_avg'] = (
            (request.state.provider['latency_avg'] + latency_avg) / 2 
            if request.state.provider['latency_avg'] != 0 
            else latency_avg
        )

        sub_provider['usage'] = sub_provider.get('usage', 0) + 1
        sub_provider['last_usage'] = time.time()

        await provider_manager.update_provider(self.config.name, request.state.provider)
        await self._update_sub_provider(sub_provider['api_key'], sub_provider)
        await self._update_user_credits(request, request.state.token_count + token_count)

    async def _update_streaming_metrics(
        self,
        request: Request,
        sub_provider: Dict[str, Any],
        start: float
    ) -> None:
        elapsed = time.time() - start

        request.state.provider['usage'] += 1
        request.state.provider['latency_avg'] = (
            (request.state.provider['latency_avg'] + elapsed) / 2 
            if request.state.provider['latency_avg'] != 0 
            else elapsed
        )

        sub_provider['usage'] = sub_provider.get('usage', 0) + 1
        sub_provider['last_usage'] = time.time()

        await provider_manager.update_provider(self.config.name, request.state.provider)
        await self._update_sub_provider(sub_provider['api_key'], sub_provider)

    async def _process_stream_chunk(
        self,
        request: Request,
        line: str
    ) -> Tuple[str, int]:
        parsed_chunk = {
            'provider_id': self.api_config.provider_id,
            **ujson.loads(line[6:].strip())
        }
        token_count = sum(
            request_processor.count_tokens(choice['delta'].get('content', ''))
            for choice in parsed_chunk['choices']
        )

        await self._update_user_credits(request, token_count)

        return f'data: {ujson.dumps(parsed_chunk)}\n\n', 200

    async def _update_user_credits(self, request: Request, token_count: int) -> None:
        request.state.user['credits'] -= token_count
        await user_manager.update_user(request.state.user['user_id'], request.state.user)