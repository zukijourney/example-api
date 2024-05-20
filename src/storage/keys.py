import motor.motor_asyncio
import ujson
from typing import List

with open("values/config.json", "r") as f:
    config = ujson.load(f)

client = motor.motor_asyncio.AsyncIOMotorClient(config["mongoURI"])
db = client["db"]["keys"]

class KeyManager:
    """
    Class for retrieving provider keys from the MongoDB database using Motor
    """

    @classmethod
    async def get_keys(cls, key_type: str):
        """Returns a list of keys for a given key type"""
        keys = await db.find_one({"name": key_type})
        return keys.get("keys") if keys else []
    
    @classmethod
    async def save_keys(cls, key_type: str, keys: List[str]):
        """Saves a list of keys for a given key type"""
        await db.update_one({"name": key_type}, {"$set": {"keys": keys}}, upsert=True)
        return