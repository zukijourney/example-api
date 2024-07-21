import typing
from prisma.models import Provider
from ..constants import DB

class ProviderManager:
    """ 
    A class for managing providers in the database.

    It uses the Prisma ORM with a CockroachDB SQL database.
    """
    
    def get_availability_percentage(self, provider: Provider) -> float:
        """Returns the availability percentage of the provider."""
        return provider.usage / provider.failures / 100 if provider.usage > 0 else 100

    async def get_providers() -> typing.List[Provider]:
        """Gets all providers from the database."""
        return await DB.provider.find_many()

    @classmethod
    async def get_best_provider_by_model(cls, model: str) -> Provider:
        """Gets the best provider by model from the database."""

        providers = [
            provider for provider in await cls.get_providers()
            for provider_model in provider.models if model in provider_model
        ]
        
        providers.sort(key=lambda provider: (
            -provider.usage,
            cls.get_availability_percentage()
        ), reverse=True)

        return providers[0]
    
    @staticmethod
    async def update_provider(provider: Provider) -> Provider:
        """Updates a provider in the database."""
        return await DB.provider.update(
            where={"id": provider.id},
            data=provider
        )