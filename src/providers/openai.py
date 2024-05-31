import openai
from typing import Union
from fastapi.responses import StreamingResponse, Response, ORJSONResponse
from ..database import KeyManager
from ..responses import streaming_chat_response, normal_chat_response
from ..utils import handle_errors

class OpenAI:
    """
    Default OpenAI provider
    """

    _key_index = 0

    @classmethod
    async def get_valid_key(cls) -> str:
        """Returns a random OpenAI key from the database using round-robin load balancing"""
        keys = await KeyManager.get_keys("openai")
        chosen_key = keys[cls._key_index]
        cls._key_index = (cls._key_index + 1) % len(keys)
        return chosen_key

    @classmethod
    @handle_errors
    async def chat_completion(cls, body: dict) -> Union[ORJSONResponse, StreamingResponse]:
        """Performs a chat completion request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_valid_key()))
        response = await client.chat.completions.create(**body)
        return await streaming_chat_response(response, body) if body.get("stream") \
            else ORJSONResponse(await normal_chat_response(response.choices[0].message.content, body))

    @classmethod
    @handle_errors
    async def image(cls, body: dict) -> ORJSONResponse:
        """Performs an image generation request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_valid_key()))
        response = await client.images.generate(**body)
        return ORJSONResponse(response.model_dump())

    @classmethod
    @handle_errors
    async def moderation(cls, body: dict) -> ORJSONResponse:
        """Performs a moderation request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_valid_key()))
        response = await client.moderations.create(**body)
        return ORJSONResponse(response.model_dump())

    @classmethod
    @handle_errors
    async def embedding(cls, body: dict) -> ORJSONResponse:
        """Performs an embedding request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_valid_key()))
        response = await client.embeddings.create(**body)
        return ORJSONResponse(response.model_dump())

    @classmethod
    @handle_errors
    async def tts(cls, body: dict) -> Response:
        """Performs a TTS request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_valid_key()))
        response = await client.audio.speech.create(**body)
        return Response(
            content=response.content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment;filename=audio.mp3"},
            status_code=200
        )