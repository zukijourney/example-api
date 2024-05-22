from litestar import post
from ..guards import auth_guard, ratelimit_guard
from ..typings import ModerationBody
from ..utils import AIModel, body_validator
from ..responses import PrettyJSONResponse

@post("/v1/moderations", guards=[auth_guard, ratelimit_guard], before_request=body_validator)
async def moderation(data: ModerationBody) -> PrettyJSONResponse:
    """Moderation endpoint request handler"""
    return await (AIModel.get_random_provider(data.model))(data.__dict__.copy())