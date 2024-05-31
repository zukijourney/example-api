from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse, ORJSONResponse
from typing import Union
from ..utils import AIModel, InvalidRequestException
from ..typings import ChatBody
from ..dependencies import auth, rate_limit
from ..database import UserManager

router = APIRouter()

@router.post("/v1/chat/completions", dependencies=[Depends(auth), Depends(rate_limit)], response_model=None)
async def chat(request: Request, data: ChatBody) -> Union[StreamingResponse, ORJSONResponse]:
    """Chat endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)
    premium_check = await UserManager.get_property(key, "premium")
    is_premium_model = data.model in AIModel.get_premium_models()

    if not premium_check and is_premium_model:
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_provider(data.model))(data.model_dump())