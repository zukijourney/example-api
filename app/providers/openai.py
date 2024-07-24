import openai
import typing
import logging
import time
from openai.types.chat import ChatCompletionChunk
from litestar.response import Stream
from ..routes import Chat, Image
from ..db import ProviderManager
from ..responses import PrettyJSONResponse

class OpenAI:
    """
    Provider class for interacting with the OpenAI API.
    """

    provider_name = "openai"
    ai_models = [
        {"id": "gpt-3.5-turbo", "type": "chat.completions", "premium": False},
        {"id": "gpt-3.5-turbo-1106", "type": "chat.completions", "premium": False},
        {"id": "gpt-3.5-turbo-0125", "type": "chat.completions", "premium": False},
        {"id": "gpt-4", "type": "chat.completions", "premium": False},
        {"id": "gpt-4-0314", "type": "chat.completions", "premium": False},
        {"id": "gpt-4-0613", "type": "chat.completions", "premium": False},
        {"id": "gpt-4-1106-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-0125-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-turbo-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-turbo", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-turbo-2024-04-09", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o-2024-05-13", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o-mini", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o-mini-2024-07-18", "type": "chat.completions", "premium": True},
        {"id": "dall-e-2", "type": "images.generations", "premium": False},
        {"id": "dall-e-3", "type": "images.generations", "premium": True}
    ]

    async def stream_response(response: openai.AsyncStream[ChatCompletionChunk], headers: dict[str, str]) -> Stream:
        """Streams the response from the OpenAI API."""

        async def async_generator():
            async for chunk in response:
                yield b"data: " + chunk.model_dump_json().encode() + b"\n\n"

        return Stream(content=async_generator(), media_type="text/event-stream", status_code=200, headers=headers)

    @classmethod
    async def chat_completion(cls, body: Chat) -> typing.Union[dict, PrettyJSONResponse]:
        """Creates a chat completion using the OpenAI API."""

        provider = await ProviderManager.get_best_provider_by_model(body.model)

        try:
            client = openai.AsyncOpenAI(
                api_key=provider.api_key,
                base_url=provider.api_url
            )

            start = time.time()

            response = await client.chat.completions.create(**body.model_dump(mode="json"))
            
            provider.usage += 1
            await ProviderManager.update_provider(provider)

            response_headers = {
                "X-Provider-Name": provider.name,
                "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
            }

            return await cls.stream_response(response, response_headers) if body.stream \
                else PrettyJSONResponse(response.model_dump(mode="json"), status_code=200, headers=response_headers)
        except openai.OpenAIError as error:
            logging.error(error)

            provider.failures += 1
            provider.usage += 1
            await ProviderManager.update_provider(provider)

            return PrettyJSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "unexpected_error",
                        "param": None,
                        "code": 500
                    }
                },
                status_code=500
            )

    @classmethod
    async def image_generation(cls, body: Image) -> typing.Union[dict, PrettyJSONResponse]:
        """Creates a chat completion using the OpenAI API."""

        provider = await ProviderManager.get_best_provider_by_model(body.model)

        try:
            client = openai.AsyncOpenAI(
                api_key=provider.api_key,
                base_url=provider.api_url
            )

            start = time.time()

            response = await client.images.generate(**body.model_dump(mode="json"))

            response_headers = {
                "X-Provider-Name": provider.name,
                "X-Processing-Ms": str(round((time.time() - start) * 1000, 0))
            }

            return PrettyJSONResponse(response.model_dump(mode="json"), status_code=200, headers=response_headers)
        except openai.OpenAIError as error:
            logging.error(error)

            provider.failures += 1
            await ProviderManager.update_provider(provider)

            return PrettyJSONResponse(
                content={
                    "error": {
                        "message": "We're sorry, something went wrong. Please try again later.",
                        "type": "unexpected_error",
                        "param": None,
                        "code": 500
                    }
                },
                status_code=500
            )