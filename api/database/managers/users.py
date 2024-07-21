import typing
import random
import string
from prisma.models import User
from ..constants import DB

class UserManager:
    """ 
    A class for managing users in the database.

    It uses the Prisma ORM with a CockroachDB SQL database.
    """

    def generate_key() -> str:
        """Generates an API key for an user."""
        return f"sk-{''.join(random.choices(string.ascii_letters + string.digits, k=48))}"

    @classmethod
    async def create_user(cls, user: str) -> User:
        """Creates a new user in the database."""
        return await DB.user.create(data={
            "name": user,
            "key": cls.generate_key(),
            "premium": False,
            "banned": False
        })

    @staticmethod
    async def delete_user(property: typing.Literal["name", "key"], value: str) -> typing.Optional[User]:
        """Deletes a user from the database."""
        return await DB.user.delete(where={property: value})
    
    @staticmethod
    async def get_user(property: typing.Literal["name", "key"], value: str) -> typing.Optional[User]:
        """Gets a user from the database."""
        return await DB.user.find_first(where={property: value})

    @staticmethod
    async def update_user(property: typing.Literal["name", "key"], value: str, data: dict) -> typing.Optional[User]:
        """Updates a user in the database."""
        return await DB.user.update(where={property: value}, data=data)