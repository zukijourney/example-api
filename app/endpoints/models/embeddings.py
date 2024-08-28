import pydantic
import typing

T = typing.TypeVar("T", str, typing.List[str], typing.Iterable[int], typing.Iterable[typing.Iterable[int]])

class Embeddings(pydantic.BaseModel):
    """
    Represents the default embeddings payload format for the API.
    """

    model: str
    input: T
    dimensions: typing.Optional[int] = None

    @pydantic.field_validator("input")
    @classmethod
    def validate_input(cls, value: T) -> T:
        if len(value) < 1:
            raise ValueError("The input field must not have an empty entry.")
        return value