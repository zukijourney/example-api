import pydantic
import typing
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam
)
from ..utils import get_all_models
from ...responses import PrettyJSONResponse

class Chat(pydantic.BaseModel):
    """
    Represents the default chat payload format for the API.
    """

    model: str
    messages: typing.List[ChatCompletionMessageParam]
    stream: bool = False
    temperature: float = 1.0
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    max_tokens: int = 1024
    tool_choice: ChatCompletionToolChoiceOptionParam
    tools: typing.List[ChatCompletionToolParam]

    @pydantic.field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> typing.Union[str, PrettyJSONResponse]:
        if value not in get_all_models():
            return PrettyJSONResponse(
                content={
                    "error": {
                        "message": f"Model '{value}' not found.",
                        "type": "invalid_request_error",
                        "param": "model",
                        "code": None
                    }
                },
                status_code=404
            )
        return value