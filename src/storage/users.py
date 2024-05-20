import motor.motor_asyncio
import ujson
from ..utils import gen_random_string

with open("values/config.json", "r") as f:
    config = ujson.load(f)

client = motor.motor_asyncio.AsyncIOMotorClient(config["mongoURI"])
db = client["db"]["users"]

class UserManager:
    """
    Class for handling user-related data in the MongoDB database using Motor
    """

    @classmethod
    async def create_key(cls, user_id: int):
        """Creates a new key for a user"""
        key = gen_random_string("zj-", length=47)
        data = {"id": str(user_id), "key": key, "usage": 0}
        await db.insert_one(data)
        return key

    @classmethod
    async def delete_key(cls, user_id: int):
        """Deletes the key of a user"""
        await db.delete_one({"id": str(user_id)})
        return

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        """Returns a user by its ID"""
        user = await db.find_one({"id": str(user_id)})
        return user.get("key") if user else None

    @classmethod
    async def check_key(cls, key: str):
        """Checks if a key exists in the database"""
        user = await db.find_one({"key": key})
        return user