from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from ..exceptions import DatabaseError
from ...config import settings

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

user_manager = UserManager()