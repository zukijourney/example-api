from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import Union, List
from ....responses import JSONResponse
from ...dependencies import DEPENDENCIES
from ....models import ChatRequest, Message
from ....utils import request_processor
from ....core import provider_manager
from ....providers import BaseProvider
from ...exceptions import InsufficientCreditsError, NoProviderAvailableError

router = APIRouter(prefix='/v1')

class ChatCompletionsHandler:
    @staticmethod
    def _has_vision_requirement(messages: List[Message]) -> bool:
        return any(
            isinstance(message.content, list) and 
            any(content.type == 'image_url' for content in message.content)
            for message in messages
        )

    @staticmethod
    def _validate_credits(available_credits: int, required_tokens: int) -> None:
        if required_tokens > available_credits:
            raise InsufficientCreditsError(
                available_credits=available_credits,
                required_tokens=required_tokens
            )

    @staticmethod
    async def _get_provider(
        model: str,
        vision_required: bool,
        tools_required: bool
    ) -> dict:
        provider = await provider_manager.get_best_provider(
            model=model,
            vision=vision_required,
            tools=tools_required
        )
        
        if not provider:
            raise NoProviderAvailableError()
            
        return provider

@router.post('/chat/completions', dependencies=DEPENDENCIES, response_model=None)
async def chat_completions(
    request: Request,
    data: ChatRequest
) -> Union[JSONResponse, StreamingResponse]:
    try:
        token_count = request_processor.count_tokens(data)
        
        ChatCompletionsHandler._validate_credits(
            available_credits=request.state.user['credits'],
            required_tokens=token_count
        )

        request.state.token_count = token_count

        vision_required = ChatCompletionsHandler._has_vision_requirement(data.messages)
        
        provider = await ChatCompletionsHandler._get_provider(
            model=data.model,
            vision_required=vision_required,
            tools_required=data.tool_choice and data.tools
        )
        
        request.state.provider = provider
        
        provider_instance = BaseProvider.get_provider_class(provider['name'])
        return await provider_instance.chat_completions(
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