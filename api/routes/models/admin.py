import pydantic
import typing

class Admin(pydantic.BaseModel):
    """
    Represents the default admin payload format for the API.
    """

    name: typing.Optional[str] = None
    key: typing.Optional[str] = None
    data: dict