import time
import ujson
import random
import string
import functools
import httpx
from dataclasses import dataclass
from fastapi import Request, Response
from typing import List, Dict, Any, Callable, Coroutine, Optional
from ..core import settings

@dataclass
class WebhookConfig:
    success_color: int = 0x00FF00
    error_color: int = 0xFF0000
    admin_id: str = '325699845031723010'
    error_alert: str = '⚠️ **Error Alert**'

class ErrorHandler:
    @staticmethod
    def retry_provider(max_retries: int) -> Callable[..., Callable]:
        def wrapper(
            func: Callable[..., Coroutine[Any, Any, Response]]
        ) -> Callable[..., Coroutine[Any, Any, Any]]:
            @functools.wraps(func)
            async def inner(*args, **kwargs) -> Any:
                for attempt in range(max_retries):
                    response = await func(*args, **kwargs)

                    if response.status_code == 200 or attempt == max_retries - 1:
                        return response

            return inner
        return wrapper

class MessageFormatter:
    @staticmethod
    def format_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        return '\n'.join(
            content_part['text']
            for content_part in content
            if content_part['type'] == 'text'
        )

    @staticmethod
    def format_messages(messages: List[Dict[str, Any]]) -> str:
        return '\n'.join(
            f'{msg['role']}: {MessageFormatter.format_content(msg['content'])}'
            for msg in messages
        )

class ResponseGenerator:
    @staticmethod
    def generate_error(message: str, provider_id: str) -> str:
        error_response = {
            'error': {
                'message': message,
                'provider_id': provider_id,
                'type': 'invalid_response_error',
                'code': 500
            }
        }
        return ResponseGenerator._serialize_json(error_response)

    @staticmethod
    def generate_chunk(
        content: str,
        model: str,
        system_fp: str,
        completion_id: str,
        provider_id: str
    ) -> str:
        chunk_response = {
            'provider_id': provider_id,
            'id': completion_id,
            'object': 'chat.completion.chunk',
            'created': int(time.time()),
            'model': model,
            'choices': [
                {
                    'index': 0,
                    'delta': {
                        'role': 'assistant',
                        'content': content
                    }
                }
            ],
            'system_fingerprint': system_fp
        }
        return ResponseGenerator._serialize_json(chunk_response, False)

    @staticmethod
    def _serialize_json(obj: Dict[str, Any], indented: bool = True) -> str:
        if indented:
            return ujson.dumps(
                obj=obj,
                ensure_ascii=False,
                allow_nan=False,
                indent=4,
                separators=(', ', ': '),
                escape_forward_slashes=False
            )

        return ujson.dumps(
            obj=obj,
            ensure_ascii=False,
            allow_nan=False,
            escape_forward_slashes=False
        )

class IDGenerator:
    COMPLETION_PREFIX = 'chatcmpl-AXb'
    FINGERPRINT_PREFIX = 'fp_'
    
    @staticmethod
    def generate_random_string(length: int, chars: str) -> str:
        return ''.join(random.choices(chars, k=length))

    @classmethod
    def generate_completion_id(cls) -> str:
        return f'{cls.COMPLETION_PREFIX}{cls.generate_random_string(29, string.ascii_letters + string.digits)}'

    @classmethod
    def generate_fingerprint(cls) -> str:
        return f'{cls.FINGERPRINT_PREFIX}{cls.generate_random_string(10, string.hexdigits.lower())}'

class WebhookManager:
    def __init__(self):
        self.config = WebhookConfig()

    def _create_embed_data(
        self,
        is_error: bool,
        model: str,
        pid: str,
        user_id: str,
        exception: Optional[str] = None
    ) -> Dict[str, Any]:
        return {
            'title': 'Status Update',
            'color': self.config.error_color if is_error else self.config.success_color,
            'fields': [
                {
                    'name': 'Status',
                    'value': 'Failed' if is_error else 'Success',
                    'inline': True
                },
                {
                    'name': 'Model',
                    'value': model,
                    'inline': True
                },
                {
                    'name': 'Error',
                    'value': exception if exception else 'No Error.',
                    'inline': True
                },
                {
                    'name': 'PID',
                    'value': pid if pid else 'No PID.',
                    'inline': True
                },
                {
                    'name': 'User',
                    'value': f'<@{user_id}>',
                    'inline': True
                }
            ],
            'footer': {
                'text': f'Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}'
            }
        }

    def _create_payload(
        self,
        is_error: bool,
        embed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = {'embeds': [embed_data]}
        
        if is_error:
            payload['content'] = f'{self.config.error_alert} <@{self.config.admin_id}>: WAKE THE FUCK UP'
        
        return payload

    @classmethod
    async def send_to_webhook(
        cls,
        request: Request,
        is_error: bool,
        model: str,
        pid: str,
        exception: Optional[str] = None
    ) -> None:
        instance = cls()

        embed_data = instance._create_embed_data(
            is_error=is_error,
            model=model,
            pid=pid,
            user_id=request.state.user['user_id'],
            exception=exception
        )
        
        payload = instance._create_payload(is_error, embed_data)

        async with httpx.AsyncClient() as client:
            await client.post(settings.webhook_url, json=payload)