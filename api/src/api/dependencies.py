import time
from fastapi import Request, Depends
from typing import Set
from .exceptions import AuthenticationError, AccessError, ValidationError
from ..core import user_manager
from ..providers import BaseProvider

class AuthenticationHandler:
    @staticmethod
    async def _get_api_key(request: Request) -> str:
        key = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not key:
            raise AuthenticationError('You need to provide a valid API key.')
        return key

    @staticmethod
    async def _validate_user(key: str) -> dict:
        user = await user_manager.get_user(key=key)
        if not user:
            raise AuthenticationError('The key you provided is invalid.')
        
        if user['banned']:
            raise AuthenticationError(
                'The key you provided is banned.',
                status_code=403
            )
        
        return user

class UserAccessHandler:
    @staticmethod
    async def _check_premium_status(user: dict) -> None:
        if user['premium_tier'] > 0 and time.time() > user['premium_expiry']:
            user['premium_tier'] = 0
            await user_manager.update_user(user['user_id'], {'premium_tier': 0})

    @staticmethod
    async def _validate_ip(request: Request, user: dict) -> None:
        if user['premium_tier'] == 0:
            current_ip = request.headers.get('CF-Connecting-IP')

            if not user['ip']:
                user['ip'] = current_ip
                await user_manager.update_user(user['user_id'], {'ip': current_ip})
            
            if user['ip'] != current_ip:
                raise AccessError('Your IP is different than the locked one.')

class RequestValidator:
    @staticmethod
    def _get_model_sets() -> tuple[Set[str], Set[str], Set[str]]:
        providers = BaseProvider.__subclasses__()
        all_models = set(BaseProvider.get_all_models())
        paid_models = {
            model for provider in providers
            for model in provider.config.paid_models
        }
        return all_models, paid_models

    @staticmethod
    async def _get_request_body(request: Request) -> dict:
        try:
            if request.headers.get('Content-Type') == 'application/json':
                return await request.json()
            elif request.headers.get('Content-Type').startswith('multipart/form-data'):
                return await request.form()
        except Exception:
            raise ValidationError('Invalid body.')

    @staticmethod
    def _validate_model_access(
        model: str,
        user_tier: int,
        all_models: Set[str],
        paid_models: Set[str],
    ) -> None:
        if model not in all_models:
            raise ValidationError(f'The model `{model}` does not exist.')
        
        if model in paid_models and user_tier == 0:
           raise ValidationError(f'You don\'t have permission to use `{model}`.')

async def authentication(request: Request) -> None:
    key = await AuthenticationHandler._get_api_key(request)
    user = await AuthenticationHandler._validate_user(key)
    request.state.user = user

async def validate_user_access(request: Request) -> None:
    user = request.state.user
    await UserAccessHandler._check_premium_status(user)
    await UserAccessHandler._validate_ip(request, user)

async def validate_request_body(request: Request) -> None:
    body = await RequestValidator._get_request_body(request)
    model = body.get('model')
    all_models, paid_models = RequestValidator._get_model_sets()
    
    RequestValidator._validate_model_access(
        model=model,
        user_tier=request.state.user.get('premium_tier', 0),
        all_models=all_models,
        paid_models=paid_models
    )

DEPENDENCIES = [
    Depends(authentication),
    Depends(validate_user_access),
    Depends(validate_request_body)
]