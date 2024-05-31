from fastapi import APIRouter, Request, Depends
from fastapi.responses import ORJSONResponse
from ..dependencies import auth, rate_limit
from ..typings import ImageBody
from ..utils import AIModel, InvalidRequestException
from ..database import UserManager

router = APIRouter()

@router.post("/v1/images/generations", dependencies=[Depends(auth), Depends(rate_limit)], response_model=None)
async def images(request: Request, data: ImageBody) -> ORJSONResponse:
    """Image endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)
    premium_check = await UserManager.get_property(key, "premium")
    is_premium_model = data.model in AIModel.get_premium_models("images.generations")

    if not premium_check and is_premium_model:
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_provider(data.model))(data.model_dump())