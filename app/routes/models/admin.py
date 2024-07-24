import pydantic
import typing

class UserInfo(pydantic.BaseModel):
    """
    Represents the user info property format in the admin payload for the API.
    """

    premium: typing.Optional[bool] = None
    banned: typing.Optional[bool] = None

class Admin(pydantic.BaseModel):
    """
    Represents the default admin payload format for the API.
    """

    name: typing.Optional[str] = None
    key: typing.Optional[str] = None
    user_info: UserInfo