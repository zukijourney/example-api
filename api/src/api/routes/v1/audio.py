from fastapi import APIRouter, Request, Response, UploadFile, File, Form, HTTPException
from ...dependencies import DEPENDENCIES
from ....models import SpeechRequest
from ....core import provider_manager
from ....providers import BaseProvider
from ...exceptions import InsufficientCreditsError, NoProviderAvailableError

router = APIRouter(prefix='/v1')

class AudioHandler:
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

@router.post('/audio/speech', dependencies=DEPENDENCIES, response_model=None)
async def audio_speech(
    request: Request,
    data: SpeechRequest
) -> Response:
    try:
        provider = await AudioHandler._get_provider(data.model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = AudioHandler._get_token_count(
            provider_instance=provider_instance,
            model=data.model
        )

        AudioHandler._validate_credits(
            available_credits=request.state.user['credits'],
            required_tokens=token_count
        )

        request.state.provider = provider

        return await provider_instance.audio_speech(
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

@router.post('/audio/transcriptions', dependencies=DEPENDENCIES, response_model=None)
async def audio_transcriptions(
    request: Request,
    model: str = Form(...),
    file: UploadFile = File(...)
) -> Response:
    try:
        provider = await AudioHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = AudioHandler._get_token_count(
            provider_instance=provider_instance,
            model=model
        )

        AudioHandler._validate_credits(
            available_credits=request.state.user['credits'],
            required_tokens=token_count
        )

        request.state.provider = provider

        return await provider_instance.audio_transcriptions(
            request,
            model,
            file
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

@router.post('/audio/translations', dependencies=DEPENDENCIES, response_model=None)
async def audio_translations(
    request: Request,
    model: str = Form(...),
    file: UploadFile = File(...)
) -> Response:
    try:
        provider = await AudioHandler._get_provider(model)
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        
        token_count = AudioHandler._get_token_count(
            provider_instance=provider_instance,
            model=model
        )

        AudioHandler._validate_credits(
            available_credits=request.state.user['credits'],
            required_tokens=token_count
        )

        request.state.provider = provider

        return await provider_instance.audio_translations(
            request,
            model,
            file
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