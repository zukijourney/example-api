import pydantic
import typing
import openai.types.chat

class Chat(pydantic.BaseModel):
    """
    Represents the default chat payload format for the API.
    """

    model: str
    messages: typing.List[openai.types.chat.ChatCompletionMessageParam]
    stream: bool = False
    temperature: float = 1.0
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    max_tokens: int = 4096
    n: int = 1
    logit_bias: typing.Optional[typing.Dict[str, int]] = None
    response_format: typing.Optional[openai.types.chat.completion_create_params.ResponseFormat] = None
    tool_choice: typing.Optional[openai.types.chat.ChatCompletionToolChoiceOptionParam] = None
    tools: typing.Optional[typing.List[openai.types.chat.ChatCompletionToolParam]] = None

    @pydantic.field_validator("messages")
    @classmethod
    def validate_messages(cls, value: list) -> typing.List[openai.types.chat.ChatCompletionMessageParam]:
        if not value:
            raise ValueError("The messages field must not have an empty array.")
        return value