import time
import secrets
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from .exceptions import DatabaseError
from ..config import settings

class UserDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.db_url)
        self.collection = self.client['db']['users']

class UserManager:
    def __init__(self):
        self.db = UserDatabase()

    async def get_user(
        self,
        user_id: Optional[int] = None,
        key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            query = {'user_id': user_id} if user_id else {'key': key}
            return await self.db.collection.find_one(query)
        except Exception as e:
            raise DatabaseError(f'Failed to retrieve user: {str(e)}')

    async def update_user(
        self,
        user_id: str,
        new_data: Dict[str, Any],
        upsert: bool = True
    ) -> Optional[Dict[str, Any]]:
        try:
            update_data = {k: v for k, v in new_data.items() if k != '_id'}
            
            return await self.db.collection.find_one_and_update(
                filter={'user_id': user_id},
                update={'$set': update_data},
                upsert=upsert,
                return_document=True
            )
        except Exception as e:
            raise DatabaseError(f'Failed to update user: {str(e)}')

    async def insert_user(self, id: int) -> Optional[Dict[str, Any]]:
        try:
            insert_data = {
                'user_id': id,
                'key': f'zu-{"".join(secrets.token_hex(16))}',
                'premium_tier': 0,
                'banned': False,
                'credits': 42069,
                'premium_expiry': 0,
                'last_daily': time.time(),
                'ip': None
            }
            await self.db.collection.insert_one(insert_data)
            return insert_data
        except Exception as e:
            raise DatabaseError(f'Failed to insert user: {str(e)}')

    async def delete_user(self, user_id: str) -> None:
        try:
            await self.db.collection.delete_one({'user_id': user_id})
        except Exception as e:
            raise DatabaseError(f'Failed to delete user: {str(e)}')