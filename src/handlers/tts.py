from litestar import post, Response, Request
from ..guards import auth_guard, ratelimit_guard
from ..typings import TTSBody
from ..utils import AIModel, InvalidRequestException
from ..database import UserManager

@post("/v1/audio/speech", guards=[auth_guard, ratelimit_guard])
async def tts(request: Request, data: TTSBody) -> Response:
    """TTS endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)

    if not (await UserManager.get_property(key, "premium")) and data.model in AIModel.get_premium_models("audio.speech"):
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_random_provider(data.model))(data.model_dump())