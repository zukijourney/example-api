import ujson
from pymongo import MongoClient
from typing import Literal, Union, Dict
from asgiref.sync import sync_to_async
from ..utils import gen_random_string

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

class UserManager:
    """
    Class for handling user-related data in the MongoDB database using Motor
    """

    client = MongoClient(config["mongoURI"])
    db = client["db"]["users"]

    @classmethod
    async def create_key(cls, user_id: int) -> str:
        """Creates a new key for an user"""
        key = gen_random_string("zj-", length=47)
        await sync_to_async(cls.db.insert_one)({"id": str(user_id), "key": key, "banned": False, "premium": False})
        return key

    @classmethod
    async def delete_key(cls, user_id: int) -> None:
        """Deletes the key of an user"""
        await sync_to_async(cls.db.delete_one)({"id": str(user_id)})
        return

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Union[Dict[str, Union[str, bool]], None]:
        """Returns an user by its ID"""
        user = await sync_to_async(cls.db.find_one)({"id": str(user_id)})
        return user.get("key") if user else None

    @classmethod
    async def check_key(cls, key: str) -> Union[dict, None]:
        """Checks if a key exists in the database"""
        user = await sync_to_async(cls.db.find_one)({"key": key})
        return user
    
    @classmethod
    async def get_property(cls, key: str, property: Literal["premium", "banned"]) -> Union[bool, None]:
        """Gets an user's property (premium or banned)"""
        user = await sync_to_async(cls.db.find_one)({"key": key})
        return user.get(property) if user else None
    
    @classmethod
    async def set_property(cls, user_id: int, property: Literal["premium", "banned"], value: bool) -> None:
        """Updates an user's property (premium or banned)"""
        await sync_to_async(cls.db.find_one_and_update)({"id": str(user_id)}, {"$set": {property: value}})
        return