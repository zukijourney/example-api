import secrets
import string
import typing
import time
from .constants import engine
from ..models import User

T = typing.TypeVar("T", int, str)

class UserManager:
    """ 
    A class for managing users in the database.
    """

    @classmethod
    async def create_user(cls, user_id: int) -> User:
        """Creates a new user in the database."""
        return await engine.save(User(
            user_id=user_id,
            key="".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)),
            premium_tier=0,
            banned=False,
            credits=22500,
            premium_expiry=0,
            last_daily=time.time(),
            ip=None
        ))

    @staticmethod
    async def delete_user(property: typing.Literal["user_id", "key"], value: T) -> typing.Optional[User]:
        """Deletes a user from the database."""

        result = await engine.find_one(User, getattr(User, property) == value)

        if result:
            await engine.delete(result)

        return result

    @staticmethod
    async def get_user(property: typing.Literal["user_id", "key"], value: T) -> typing.Optional[User]:
        """Gets a user from the database."""
        return await engine.find_one(User, getattr(User, property) == value)

    @staticmethod
    async def update_user(property: typing.Literal["user_id", "key"], value: T, user: dict) -> typing.Optional[User]:
        """Updates a user in the database."""

        result = await engine.find_one(User, getattr(User, property) == value)

        if result:
            for key, value in user.items():
                if key != "id":
                    setattr(result, key, value)
            await engine.save(result)

        return result