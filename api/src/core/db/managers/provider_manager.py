from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from ...config import settings

class ProviderDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.db_url)
        self.collection = self.client['db']['providers']

class ProviderManager:
    def __init__(self):
        self.db = ProviderDatabase()

    @staticmethod
    def _calculate_availability(
        usage: int = 0,
        failures: int = 0
    ) -> float:
        if usage > 0:
            return ((usage - failures) / usage) * 100
        return 100.0 - failures

    @staticmethod
    def _sort_providers(
        providers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return sorted(
            providers,
            key=lambda x: (
                -ProviderManager._calculate_availability(
                    x.get('usage', 0),
                    x.get('failures', 0)
                ),
                x['usage'],
                x['latency_avg'],
                not x['supports_real_streaming']
            )
        )

    def _filter_providers(
        self,
        providers: List[Dict[str, Any]],
        vision: bool = False,
        tools: bool = False
    ) -> List[Dict[str, Any]]:
        if vision:
            providers = [p for p in providers if p['supports_vision']]
        if tools:
            providers = [p for p in providers if p['supports_tool_calling']]
        return providers

    async def get_best_provider(
        self,
        model: str,
        vision: bool = False,
        tools: bool = False
    ) -> Optional[Dict[str, Any]]:
        providers = await self.db.collection.find(
            {'models': {'$in': [model]}}
        ).to_list(length=None)

        if not providers:
            return None

        sorted_providers = self._sort_providers(providers)
        filtered_providers = self._filter_providers(
            sorted_providers,
            vision=vision,
            tools=tools
        )

        return filtered_providers[0] if filtered_providers else None

    async def update_provider(
        self,
        name: str,
        new_data: Dict[str, Any]
    ) -> None:
        update_data = {k: v for k, v in new_data.items() if k != '_id'}
        
        await self.db.collection.find_one_and_update(
            filter={'name': name},
            update={'$set': update_data},
            upsert=True
        )

provider_manager = ProviderManager()