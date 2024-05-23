from litestar import post, Request
from ..guards import auth_guard, ratelimit_guard
from ..typings import ModerationBody
from ..utils import AIModel, InvalidRequestException
from ..responses import PrettyJSONResponse
from ..database import UserManager

@post("/v1/moderations", guards=[auth_guard, ratelimit_guard])
async def moderation(request: Request, data: ModerationBody) -> PrettyJSONResponse:
    """Moderation endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)

    if not (await UserManager.get_property(key, "premium")) and data.model in AIModel.get_premium_models("moderation"):
        return InvalidRequestException("This model is not available in the free tier.", status_code=402).to_response()

    return await (AIModel.get_random_provider(data.model))(data.model_dump())