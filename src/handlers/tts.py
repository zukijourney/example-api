from litestar import post, Response
from ..guards import auth_guard, ratelimit_guard
from ..typings import TTSBody
from ..utils import AIModel

@post("/v1/audio/speech", guards=[auth_guard, ratelimit_guard])
async def tts(data: TTSBody) -> Response:
    """TTS endpoint request handler"""
    return await (AIModel.get_random_provider(data.model))(data.__dict__.copy())