import openai
import traceback
from typing import Union
from litestar.response import Stream, Response
from ..database import KeyManager
from ..responses import PrettyJSONResponse, streaming_chat_response, normal_chat_response
from ..utils import make_response

class OpenAI:
    """
    Default OpenAI provider
    """

    _key_index = 0

    @classmethod
    async def get_random_key(cls) -> str:
        """Returns a random OpenAI key from the database using round-robin load balancing"""
        keys = await KeyManager.get_keys("openai")
        chosen_key = keys[cls._key_index]
        cls._key_index = (cls._key_index + 1) % len(keys)
        return chosen_key

    @classmethod
    async def chat_completion(cls, body: dict) -> Union[PrettyJSONResponse, Stream]:
        """Performs a chat completion request"""

        if not body.get("tools"):
            body.pop("tool_choice", None)

        try:
            client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
            response = await client.chat.completions.create(**body)
            return await streaming_chat_response(response, body) if body.get("stream") \
                else PrettyJSONResponse(await normal_chat_response(response.choices[0].message.content, body))
        except openai.APIStatusError:
            traceback.print_exc()
            return make_response(
                message="We were unable to generate a response. Please try again later.",
                error_type="invalid_response_error",
                status_code=500
            )

    @classmethod
    async def image(cls, body: dict) -> PrettyJSONResponse:
        """Performs an image generation request"""
        try:
            client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
            response = await client.images.generate(**body)
            return PrettyJSONResponse(response.model_dump(), status_code=200)
        except openai.APIStatusError:
            traceback.print_exc()
            return make_response(
                message="We were unable to generate a response. Please try again later.",
                error_type="invalid_response_error",
                status_code=500
            )
        
    @classmethod
    async def moderation(cls, body: dict) -> PrettyJSONResponse:
        """Performs a moderation request"""
        try:
            client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
            response = await client.moderations.create(**body)
            return PrettyJSONResponse(response.model_dump(), status_code=200)
        except openai.APIStatusError:
            traceback.print_exc()
            return make_response(
                message="We were unable to generate a response. Please try again later.",
                error_type="invalid_response_error",
                status_code=500
            )
        
    @classmethod
    async def embedding(cls, body: dict) -> PrettyJSONResponse:
        """Performs an embedding request"""
        try:
            client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
            response = await client.embeddings.create(**body)
            return PrettyJSONResponse(response.model_dump(), status_code=200)
        except openai.APIStatusError:
            traceback.print_exc()
            return make_response(
                message="We were unable to generate a response. Please try again later.",
                error_type="invalid_response_error",
                status_code=500
            )
        
    @classmethod
    async def tts(cls, body: dict) -> Response:
        """Performs a TTS request"""
        try:
            client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
            response = await client.audio.speech.create(**body)
            return Response(
                content=response.content,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "attachment;filename=audio.mp3"},
                status_code=200
            )
        except openai.APIStatusError:
            traceback.print_exc()
            return make_response(
                message="We were unable to generate a response. Please try again later.",
                error_type="invalid_response_error",
                status_code=500
            )