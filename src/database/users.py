import pymongo
import ujson
from asgiref.sync import sync_to_async
from ..utils import gen_random_string

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

class UserManager:
    """
    Class for handling user-related data in the MongoDB database using Motor
    """

    client = pymongo.MongoClient(config["mongoURI"])
    db = client["db"]["users"]

    @classmethod
    async def create_key(cls, user_id: int):
        """Creates a new key for an user"""
        key = gen_random_string("zj-", length=47)
        await sync_to_async(cls.db.insert_one)({"id": str(user_id), "key": key, "banned": False, "premium": False})
        return key

    @classmethod
    async def delete_key(cls, user_id: int):
        """Deletes the key of an user"""
        await sync_to_async(cls.db.delete_one)({"id": str(user_id)})
        return

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        """Returns an user by its ID"""
        user = await sync_to_async(cls.db.find_one)({"id": str(user_id)})
        return user.get("key") if user else None

    @classmethod
    async def check_key(cls, key: str):
        """Checks if a key exists in the database"""
        user = await sync_to_async(cls.db.find_one)({"key": key})
        return user
    
    @classmethod
    async def get_property(cls, key: str, property: str):
        """Gets an user's property (premium or banned)"""
        user = await sync_to_async(cls.db.find_one)({"key": key})
        return user.get(property) if user else None
    
    @classmethod
    async def set_property(cls, user_id: int, property: str, value: bool):
        """Updates an user's property (premium or banned)"""
        await sync_to_async(cls.db.find_one_and_update)({"id": str(user_id)}, {"$set": {property: value}})
        return