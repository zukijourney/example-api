from fastapi import APIRouter, Request, Depends, Response
from ..dependencies import auth, rate_limit
from ..typings import TTSBody
from ..utils import AIModel, InvalidRequestException
from ..database import UserManager

router = APIRouter()

@router.post("/v1/audio/speech", dependencies=[Depends(auth), Depends(rate_limit)], response_model=None)
async def tts(request: Request, data: TTSBody) -> Response:
    """TTS endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)
    premium_check = await UserManager.get_property(key, "premium")
    is_premium_model = data.model in AIModel.get_premium_models("audio.speech")

    if not premium_check and is_premium_model:
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_provider(data.model))(data.model_dump())