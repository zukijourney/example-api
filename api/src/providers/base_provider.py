import os
import inspect
import importlib
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorClient
from asgiref.sync import sync_to_async
from typing import List, Dict, Optional, Type, ClassVar
from ..core import settings

@dataclass
class ProviderConfig:
    name: str
    supports_vision: bool
    supports_real_streaming: bool
    supports_tool_calling: bool
    free_models: List[str]
    paid_models: List[str]
    model_prices: Dict[str, int]

class BaseProvider:
    config: ClassVar[ProviderConfig] = ProviderConfig(
        name='',
        supports_vision=False,
        supports_real_streaming=False,
        supports_tool_calling=False,
        free_models=[],
        paid_models=[],
        model_prices={}
    )

    def __init__(self):
        self.db = AsyncIOMotorClient(settings.db_url)['db']['providers']

    @classmethod
    def get_provider_class(cls, name: str) -> Optional[Type['BaseProvider']]:
        return next(
            (p for p in cls.__subclasses__() if p.config.name == name),
            None
        )

    @classmethod
    def get_all_models(cls) -> List[str]:
        all_models = set()
        for provider in cls.__subclasses__():
            all_models.update(
                provider.config.free_models +
                provider.config.paid_models
            )
        return list(all_models)

    @sync_to_async
    def import_modules(self):
        def get_module_name(file_path: str, base_module: str) -> str:
            rel_path = os.path.relpath(os.path.dirname(file_path), package_dir)

            if rel_path == '.':
                return f'{base_module}.{os.path.splitext(os.path.basename(file_path))[0]}'

            return f'{base_module}.{rel_path.replace(os.sep, ".")}.{os.path.splitext(os.path.basename(file_path))[0]}'

        root_file = inspect.getfile(self.__class__)
        package_dir = os.path.dirname(root_file)
        base_module = self.__module__.rsplit('.', 1)[0]

        for root, _, files in os.walk(package_dir):
            python_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
            
            for file in python_files:
                file_path = os.path.join(root, file)
                module_name = get_module_name(file_path, base_module)
                importlib.import_module(module_name)

    async def sync_to_db(self) -> None:
        try:
            existing_providers = await self.db.find({}).to_list(length=None)
            existing_names = {p['name'] for p in existing_providers}

            current_names = {p.config.name for p in self.__class__.__subclasses__()}

            for obsolete_name in existing_names - current_names:
                await self.db.delete_one({'name': obsolete_name})
            
            for new_provider in current_names - existing_names:
                provider_class = self.get_provider_class(new_provider)
                config = provider_class.config
                all_models = (
                    config.free_models +
                    config.paid_models
                )
                await self.db.insert_one({
                    'name': config.name,
                    'supports_vision': config.supports_vision,
                    'supports_real_streaming': config.supports_real_streaming,
                    'supports_tool_calling': config.supports_tool_calling,
                    'models': all_models,
                    'usage': 0,
                    'failures': 0,
                    'latency_avg': 0
                })


            for provider_class in self.__class__.__subclasses__():
                config = provider_class.config
                all_models = (
                    config.free_models +
                    config.paid_models
                )

                for db_provider in existing_providers:
                    if db_provider['name'] == config.name and all_models != db_provider['models']:
                        await self.db.update_one(
                            {'name': config.name},
                            {'$set': {'models': all_models}},
                            upsert=True
                        )

        except Exception as e:
            raise Exception(f'Failed to sync providers: {str(e)}')

    @classmethod
    async def chat_completions(cls, **_) -> None:
        raise NotImplementedError

    @classmethod
    async def images_generations(cls, **_) -> None:
        raise NotImplementedError

    @classmethod
    async def embeddings(cls, **_) -> None:
        raise NotImplementedError

    @classmethod
    async def moderations(cls, **_) -> None:
        raise NotImplementedError

    @classmethod
    async def audio_speech(cls, **_) -> None:
        raise NotImplementedError
    
    @classmethod
    async def audio_transcriptions(cls, **_) -> None:
        raise NotImplementedError
    
    @classmethod
    async def audio_translations(cls, **_) -> None:
        raise NotImplementedError