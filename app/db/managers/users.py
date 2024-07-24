import sqlmodel
import typing
import random
import string
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import User
from ..utils import engine

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
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                new_user = User(name=user, key=cls.generate_key(), premium=False, banned=False)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    @staticmethod
    async def delete_user(property: typing.Literal["name", "key"], value: str) -> typing.Optional[User]:
        """Deletes a user from the database."""
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                result = (await session.exec(sqlmodel.select(User).where(getattr(User, property) == value))).first()

                if result:
                    session.delete(result)
                    await session.commit()
                    await session.refresh(result)

                return result
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    @staticmethod
    async def get_user(property: typing.Literal["name", "key"], value: str) -> typing.Optional[User]:
        """Gets a user from the database."""
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                result = await session.exec(sqlmodel.select(User).where(getattr(User, property) == value))
                return result.first()
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    @staticmethod
    async def update_user(property: typing.Literal["name", "key"], value: str, data: dict) -> typing.Optional[User]:
        """Updates a user in the database."""
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                result = (await session.exec(sqlmodel.select(User).where(getattr(User, property) == value))).first()

                if result:
                    for key, value in data.items():
                        setattr(result, key, value)

                    session.add(result)

                    await session.commit()
                    await session.refresh(result)

                return result
            except:
                await session.rollback()
                raise
            finally:
                await session.close()