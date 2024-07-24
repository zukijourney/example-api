import sqlmodel
import typing
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Provider
from ..utils import engine

class ProviderManager:
    """ 
    A class for managing providers in the database.

    It uses the Prisma ORM with a CockroachDB SQL database.
    """
    
    def get_availability_percentage(provider: Provider) -> float:
        """Returns the availability percentage of the provider."""
        if provider.usage > 0 and provider.failures > 0:
            return provider.usage / provider.failures / 100
        return 100.0

    async def get_providers() -> typing.List[Provider]:
        """Gets all providers from the database."""
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                return await session.exec(sqlmodel.select(Provider))
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    @classmethod
    async def get_best_provider_by_model(cls, model: str) -> Provider:
        """Gets the best provider by model from the database."""

        providers = [
            provider for provider in await cls.get_providers()
            for provider_model in provider.models if model in provider_model
        ]
        
        providers.sort(key=lambda provider: (
            -provider.usage,
            cls.get_availability_percentage(provider)
        ), reverse=True)

        return providers[0]
    
    @staticmethod
    async def update_provider(provider: Provider) -> typing.Optional[Provider]:
        """Updates a provider in the database."""

        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                result = (await session.exec(sqlmodel.select(Provider).where(Provider.name == provider.name))).first()

                if result:
                    for key, value in provider.model_dump(mode="json").items():
                        setattr(result, key, value)

                    session.add(result)

                    await session.commit()
                    await session.refresh(result)

                return result
            except:
                await session.rollback()
                raise
            finally:
                await session.close()