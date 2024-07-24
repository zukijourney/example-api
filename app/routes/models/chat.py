import pydantic
import typing
from openai.types import chat
from ..utils import get_all_models
from ...responses import PrettyJSONResponse

class Chat(pydantic.BaseModel):
    """
    Represents the default chat payload format for the API.
    """

    model: str
    messages: typing.List[chat.ChatCompletionMessageParam]
    stream: bool = False
    temperature: float = 1.0
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    max_tokens: int = 1024
    n: int = 1
    logit_bias: typing.Optional[typing.Dict[str, int]] = None
    response_format: typing.Optional[chat.completion_create_params.ResponseFormat] = None
    tool_choice: typing.Optional[chat.ChatCompletionToolChoiceOptionParam] = None
    tools: typing.Optional[typing.List[chat.ChatCompletionToolParam]] = None

    @pydantic.field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> typing.Union[str, PrettyJSONResponse]:
        if value not in get_all_models(type="chat.completions"):
            raise ValueError(f"Model '{value}' not found.")
        return value