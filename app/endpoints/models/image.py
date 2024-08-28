import pydantic
import typing

class Image(pydantic.BaseModel):
    """
    Represents the default image payload format for the API.
    """

    model: str
    prompt: str
    n: int = 1
    size: typing.Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "1024x1024"

    @pydantic.field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        if len(value) < 1:
            raise ValueError("The prompt field must not have an empty entry.")
        return value