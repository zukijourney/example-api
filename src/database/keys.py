import ujson
from typing import List, Optional
from pymongo import MongoClient
from asgiref.sync import sync_to_async

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

class KeyManager:
    """
    Class for retrieving provider keys from the MongoDB database using Motor
    """

    client = MongoClient(config["mongoURI"])
    db = client["db"]["keys"]

    @classmethod
    async def get_keys(cls, key_type: str) -> List[Optional[str]]:
        """Returns a list of keys for a given key type"""
        keys = await sync_to_async(cls.db.find_one)({"name": key_type})
        return keys.get("keys") if keys else []