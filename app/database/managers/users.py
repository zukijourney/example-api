import typing
from ..constants import engine
from ..models import User

class UserManager:
    """ 
    A class for managing users in the database.
    """

    @staticmethod
    async def get_user(property: typing.Literal["user_id", "key"], value: typing.Union[int, str]) -> typing.Optional[User]:
        """Gets a user from the database."""
        return await engine.find_one(User, getattr(User, property) == value)

    @staticmethod
    async def update_user(property: typing.Literal["user_id", "key"], value: typing.Union[int, str], user: dict) -> typing.Optional[User]:
        """Updates a user in the database."""

        result = await engine.find_one(User, getattr(User, property) == value)

        if result:
            for key, value in user.items():
                if key != "id":
                    setattr(result, key, value)
            await engine.save(result)

        return result