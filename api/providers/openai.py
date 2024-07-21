import openai
import typing
import logging
from openai.types.chat import ChatCompletionChunk
from litestar.response import Stream
from ..routes import Chat
from ..database import ProviderManager
from ..responses import PrettyJSONResponse

class OpenAI:
    """
    A base example provider class for interacting with the OpenAI API.
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
        {"id": "gpt-4-vision-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-1106-vision-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-0125-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-turbo-preview", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-turbo", "type": "chat.completions", "premium": True},
        {"id": "gpt-4-turbo-2024-04-09", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o-2024-05-13", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o-mini", "type": "chat.completions", "premium": True},
        {"id": "gpt-4o-mini-2024-07-18", "type": "chat.completions", "premium": True}
    ]

    async def stream_response(self, response: openai.AsyncStream[ChatCompletionChunk]) -> Stream:
        """Streams the response from the OpenAI API."""

        async def async_generator():
            async for chunk in response:
                yield chunk.model_dump_json().encode()

        return Stream(content=async_generator(), media_type="text/event-stream", status_code=200)

    @staticmethod
    async def chat_completion(body: Chat) -> typing.Union[dict, PrettyJSONResponse]:
        """Creates a chat completion using the OpenAI API."""

        provider = await ProviderManager.get_best_provider_by_model(body.model)

        try:
            client = openai.AsyncOpenAI(
                api_key=provider.api_key,
                base_url=provider.api_url
            )

            response = await client.chat.completions.create(**body.model_dump(mode="json"))

            return await OpenAI.stream_response(response) if body.stream \
                else PrettyJSONResponse(response.model_dump(mode="json"), status_code=200)
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