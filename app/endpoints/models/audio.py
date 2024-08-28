import pydantic
import typing

class Speech(pydantic.BaseModel):
    """
    Represents the default speech payload format for the API.
    """

    model: str
    input: str
    voice: typing.Optional[str] = None

    @pydantic.field_validator("input")
    @classmethod
    def validate_input(cls, value: typing.Optional[str]) -> typing.Optional[str]:
        if value:
            if len(value) < 1:
                raise ValueError("The input field must not have an empty entry.")
        return value

class Transcription(pydantic.BaseModel):
    """
    Represents the default transcription payload format for the API.
    """

    file: bytes
    model: str