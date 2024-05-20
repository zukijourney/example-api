import openai
import random
from starlette.responses import StreamingResponse
from ..storage import KeyManager
from ..responses import PrettyJSONResponse, streaming_chat_response, normal_chat_response

class OpenAI:
    """
    Example OpenAI provider
    """

    @classmethod
    async def get_random_key(cls):
        """Returns a random OpenAI key from the database"""
        keys = await KeyManager.get_keys("openai")
        return random.choice(keys)

    @classmethod
    async def chat(cls, body: dict):
        """Performs a chat completion request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
        response = await client.chat.completions.create(**body)
        return StreamingResponse(streaming_chat_response(response, body)) if body.get("stream") \
            else PrettyJSONResponse(await normal_chat_response(response.choices[0].message.content, body))

    @classmethod
    async def image(cls, body: dict):
        """Performs an image generation request"""
        client = openai.AsyncOpenAI(api_key=(await cls.get_random_key()))
        response = await client.images.generate(**body)
        return PrettyJSONResponse(response.model_dump())