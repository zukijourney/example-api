from fastapi import APIRouter, Request, HTTPException
from ....responses import JSONResponse
from ...dependencies import DEPENDENCIES
from ....models import EmbeddingsRequest
from ....core import provider_manager
from ....providers import BaseProvider
from ...exceptions import InsufficientCreditsError, NoProviderAvailableError

router = APIRouter(prefix='/v1')

class EmbeddingsHandler:
    @staticmethod
    async def _get_provider(model: str) -> dict:
        provider = await provider_manager.get_best_provider(model)
        if not provider:
            raise NoProviderAvailableError()
        return provider

    @staticmethod
    def _validate_credits(
        available_credits: int,
        required_tokens: int
    ) -> None:
        if required_tokens > available_credits:
            raise InsufficientCreditsError(
                available_credits=available_credits,
                required_tokens=required_tokens
            )

    @staticmethod
    def _get_token_count(
        provider_instance: BaseProvider,
        model: str
    ) -> int:
        return provider_instance.config.model_prices.get(model, 100)

@router.post('/embeddings', dependencies=DEPENDENCIES, response_model=None)
async def embeddings(
    request: Request,
    data: EmbeddingsRequest
) -> JSONResponse:
    try:
        provider = await EmbeddingsHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = EmbeddingsHandler._get_token_count(
            provider_instance=provider_instance,
            model=data.model
        )

        EmbeddingsHandler._validate_credits(
            available_credits=request.state.user['credits'],
            required_tokens=token_count
        )

        request.state.provider = provider

        return await provider_instance.embeddings(
            request,
            **data.model_dump(mode='json')
        )

    except (InsufficientCreditsError, NoProviderAvailableError) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail='An internal server error occurred while processing your request. Try again later.'
        )