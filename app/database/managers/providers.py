import typing
from ..constants import engine
from ..models import Provider, Model

class ProviderManager:
    """ 
    A class for managing providers in the database.
    """

    def get_availability_percentage(model: Model) -> float:
        """Returns the availability percentage of the provider."""
        if model.usage > 0 and model.failures > 0:
            return model.usage / model.failures / 100
        return 100.0

    async def get_providers() -> typing.List[Provider]:
        """Gets all providers from the database."""
        return await engine.find(Provider, {})

    @classmethod
    async def get_best_provider_by_model(cls, model_id: str, premium: bool) -> typing.Optional[Provider]:
        """Gets the best provider by model from the database."""

        providers = [
            provider for provider in await cls.get_providers()
            if any(m.api_name == model_id for m in provider.models)
            and (premium or not provider.premium_only)
        ]

        providers.sort(
            key=lambda provider: (
                min((model.usage for model in provider.models if model.api_name == model_id), default=float("inf")),
                min((cls.get_availability_percentage(model) for model in provider.models if model.api_name == model_id), default=float("inf")),
                min((model.last_failure for model in provider.models if model.api_name == model_id), default=float("inf")),
                min((model.avg_latency for model in provider.models if model.api_name == model_id), default=float("inf"))
            )
        )

        return providers[0] if len(providers) > 0 else None
    
    @staticmethod
    async def update_provider(provider: Provider) -> typing.Optional[Provider]:
        """Updates a provider in the database."""

        result = await engine.find_one(Provider, Provider.name == provider.name)

        if result:
            for key, value in provider.model_dump(mode="json").items():
                if key != "id":
                    setattr(result, key, value)
            await engine.save(result)

        return result