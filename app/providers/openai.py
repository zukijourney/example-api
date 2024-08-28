import openai
import typing
import time
import traceback
import httpx
import uuid
import aiofiles
from openai.types.chat import ChatCompletionChunk
from litestar.response import Response, Stream
from ..config import settings
from ..endpoints import Chat, Image, Embeddings, Speech, Transcription
from ..database import UserManager, ProviderManager
from ..responses import JSONResponse
from .error_handler import handle_errors

class OpenAI:
    """
    Provider class for interacting with the OpenAI API.
    """

    ai_models = [
        {"id": "gpt-3.5-turbo", "type": "chat.completions", "premium": False, "cost": "per_token", "supports_tools": True, "owner": "openai"},
        {"id": "gpt-3.5-turbo-1106", "type": "chat.completions", "premium": False, "cost": "per_token", "supports_tools": True, "owner": "openai"},
        {"id": "gpt-3.5-turbo-0125", "type": "chat.completions", "premium": False, "cost": "per_token", "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 2, "supports_tools": False, "owner": "openai"},
        {"id": "gpt-4-0613", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 2, "supports_tools": False, "owner": "openai"},
        {"id": "gpt-4-1106-preview", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.75, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4-0125-preview", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.75, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4-turbo-preview", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.75, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4-turbo", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.5, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4-turbo-2024-04-09", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.5, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4o", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.25, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4o-2024-05-13", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.25, "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4o-2024-08-06", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.25, "supports_tools": True, "owner": "openai"},
        {"id": "chatgpt-4o-latest", "type": "chat.completions", "premium": False, "cost": "per_token", "cost_multiplier": 1.25, "supports_tools": False, "owner": "openai"},
        {"id": "gpt-4o-mini", "type": "chat.completions", "premium": False, "cost": "per_token", "supports_tools": True, "owner": "openai"},
        {"id": "gpt-4o-mini-2024-07-18", "type": "chat.completions", "premium": False, "cost": "per_token", "supports_tools": True, "owner": "openai"},
        {"id": "dall-e-2", "type": "images.generations", "premium": False, "owner": "openai"},
        {"id": "dall-e-3", "type": "images.generations", "premium": True, "cost": 2500, "owner": "openai"},
        {"id": "text-embedding-ada-002", "type": "embeddings", "premium": False, "owner": "openai"},
        {"id": "text-embedding-3-small", "type": "embeddings", "premium": False, "owner": "openai"},
        {"id": "text-embedding-3-large", "type": "embeddings", "premium": False, "owner": "openai"},
        {"id": "tts-1", "type": "audio.speech", "premium": False, "cost": "per_token", "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], "owner": "openai"},
        {"id": "tts-1-hd", "type": "audio.speech", "premium": True, "cost": "per_token", "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], "owner": "openai"},
        {"id": "whisper-1", "type": "audio.transcriptions", "premium": False, "cost": "per_token", "owner": "openai"}
    ]
    
    async def stream_response(response: openai.AsyncStream[ChatCompletionChunk], headers: typing.Dict[str, str], input_tokens: int, user_key: str) -> Stream:
        """Streams the response from the OpenAI API."""

        user = await UserManager.get_user("key", user_key)
        user.credits -= input_tokens

        async def async_generator():
            nonlocal user
            async for chunk in response:
                token_count = sum(round(len(choice.delta.content) / 4) for choice in chunk.choices if choice.delta.content)
                user.credits -= token_count
                await UserManager.update_user("key", user_key, user.model_dump())
                yield b"data: " + chunk.model_dump_json().encode() + b"\n\n"

        return Stream(content=async_generator(), media_type="text/event-stream", status_code=200, headers=headers)

    @classmethod
    @handle_errors
    async def chat_completion(cls, body: Chat, user_key: str) -> typing.Union[Stream, JSONResponse]:
        """Create a chat completion using the OpenAI API."""

        user = await UserManager.get_user("key", user_key)

        provider = await ProviderManager.get_best_provider_by_model(body.model, user.premium_tier > 0)
        model = next((m for m in provider.models if m.api_name == body.model))
        client = openai.AsyncOpenAI(api_key=provider.api_key, base_url=provider.api_url)

        multiplier = next((model for model in cls.ai_models if model["id"] == body.model), None).get("cost_multiplier", 1)
        supports_tools = next((model for model in cls.ai_models if model["id"] == body.model), None).get("supports_tools")

        start = time.time()

        body.model = model.provider_name

        if not supports_tools:
            delattr(body, "tools")
            delattr(body, "tool_choice")

        try:
            response = await client.chat.completions.create(**body.model_dump())
        except openai.APIError:
            traceback.print_exc()
            model.failures += 1
            model.last_failure = time.time()
            await ProviderManager.update_provider(provider)
            return JSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "invalid_response_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=500
            )

        model.usage += 1
        latency = int(round(((time.time() - start) * 1000), 0))

        if body.stream:
            model.avg_latency = ((latency + model.avg_latency) / 2) if model.avg_latency > 0 else latency
        else:
            word_count = sum(len(choice.message.content) for choice in response.choices if choice.message.content)
            latency = int(round((((time.time() - start) * 1000) / word_count), 0))
            model.avg_latency = ((latency + model.avg_latency) / 2) if model.avg_latency > 0 else latency
        
        await ProviderManager.update_provider(provider)

        response_headers = {
            "X-Provider-Name": provider.name,
            "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
        }

        input_tokens = sum(
            round(len(content) / 4) * multiplier
            if message.get("type") == "text" and isinstance(message["content"], list)
            else 250 * multiplier
            for message in body.messages
            for content in (message["content"] if isinstance(message["content"], list) else [message["content"]])
        )
        
        if not body.stream:
            token_count = sum(round(len(choice.message.content) / 4) for choice in response.choices if choice.message.content)
            user.credits -= input_tokens + token_count
            await UserManager.update_user("key", user_key, user.model_dump())

        return await cls.stream_response(response, response_headers, input_tokens, user_key) if body.stream \
            else JSONResponse(response.model_dump(mode="json"), status_code=200, headers=response_headers)

    @classmethod
    @handle_errors
    async def image_generation(cls, body: Image, user_key: str) -> JSONResponse:
        """Create an image using the OpenAI API."""

        user = await UserManager.get_user("key", user_key)

        provider = await ProviderManager.get_best_provider_by_model(body.model, user.premium_tier > 0)
        model = next((m for m in provider.models if m.api_name == body.model))
        client = openai.AsyncOpenAI(api_key=provider.api_key, base_url=provider.api_url)
        
        cost = next((model for model in cls.ai_models if model["id"] == body.model), None).get("cost", 100)

        start = time.time()

        try:
            response = await client.images.generate(**body.model_dump(mode="json"))
        except openai.APIError:
            model.failures += 1
            model.last_failure = time.time()
            await ProviderManager.update_provider(provider)
            return JSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "invalid_response_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=500
            )

        response_headers = {
            "X-Provider-Name": provider.name,
            "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
        }

        user.credits -= cost
        await UserManager.update_user("key", user_key, user.model_dump())

        for data in response.data:
            image_name = f"{str(uuid.uuid4())}.png"

            async with httpx.AsyncClient() as client:
                image_bytes = (await client.get(data.url)).content
                async with aiofiles.open(f"/cdn/{image_name}", "wb") as f:
                    await f.write(image_bytes)

            data.url = f"{settings.cdn_url}/{image_name}"

        return JSONResponse(response.model_dump(mode="json"), status_code=200, headers=response_headers)

    @classmethod
    @handle_errors
    async def embeddings(cls, body: Embeddings, user_key: str) -> JSONResponse:
        """Create an embedding using the OpenAI API."""

        user = await UserManager.get_user("key", user_key)

        provider = await ProviderManager.get_best_provider_by_model(body.model, user.premium_tier > 0)
        model = next((m for m in provider.models if m.api_name == body.model))
        client = openai.AsyncOpenAI(api_key=provider.api_key, base_url=provider.api_url)
        
        cost = next((model for model in cls.ai_models if model["id"] == body.model), None).get("cost", 100)

        start = time.time()

        try:
            response = await client.embeddings.create(**body.model_dump(mode="json"))
        except openai.APIError:
            model.failures += 1
            model.last_failure = time.time()
            await ProviderManager.update_provider(provider)
            return JSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "invalid_response_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=500
            )

        response_headers = {
            "X-Provider-Name": provider.name,
            "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
        }

        user = await UserManager.get_user("key", user_key)
        user.credits -= cost
        await UserManager.update_user("key", user_key, user.model_dump())

        return JSONResponse(response.model_dump(mode="json"), status_code=200, headers=response_headers)

    @classmethod
    @handle_errors
    async def speech(cls, body: Speech, user_key: str) -> typing.Union[Response, JSONResponse]:
        """Create an audio speech using the OpenAI API."""

        user = await UserManager.get_user("key", user_key)

        provider = await ProviderManager.get_best_provider_by_model(body.model, user.premium_tier > 0)
        model = next((m for m in provider.models if m.api_name == body.model))
        client = openai.AsyncOpenAI(api_key=provider.api_key, base_url=provider.api_url)
        
        cost = next((model for model in cls.ai_models if model["id"] == body.model), None).get("cost", 100)

        start = time.time()

        try:
            response = await client.audio.speech.create(**body.model_dump(mode="json"))
        except openai.APIError:
            model.failures += 1
            model.last_failure = time.time()
            await ProviderManager.update_provider(provider)
            return JSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "invalid_response_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=500
            )

        response_headers = {
            "X-Provider-Name": provider.name,
            "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
        }

        user = await UserManager.get_user("key", user_key)
        user.credits -= cost
        await UserManager.update_user("key", user_key, user.model_dump())

        return Response(response, status_code=200, headers=response_headers)

    @classmethod
    @handle_errors
    async def transcription(cls, body: Transcription, user_key: str) -> JSONResponse:
        """Create an audio transcription using the OpenAI API."""

        user = await UserManager.get_user("key", user_key)

        provider = await ProviderManager.get_best_provider_by_model(body.model, user.premium_tier > 0)
        model = next((m for m in provider.models if m.api_name == body.model))
        client = openai.AsyncOpenAI(api_key=provider.api_key, base_url=provider.api_url)
        
        cost = next((model for model in cls.ai_models if model["id"] == body.model), None).get("cost", 100)

        start = time.time()

        try:
            response = await client.audio.transcriptions.create(**body.model_dump())
        except openai.APIError:
            model.failures += 1
            model.last_failure = time.time()
            await ProviderManager.update_provider(provider)
            return JSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "invalid_response_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=500
            )

        response_headers = {
            "X-Provider-Name": provider.name,
            "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
        }

        user = await UserManager.get_user("key", user_key)
        user.credits -= cost
        await UserManager.update_user("key", user_key, user.model_dump())

        return JSONResponse(response.model_dump(mode="json"), status_code=200, headers=response_headers)