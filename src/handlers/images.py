from litestar import post, Request
from ..guards import auth_guard, ratelimit_guard
from ..typings import ImageBody
from ..utils import AIModel, InvalidRequestException
from ..responses import PrettyJSONResponse
from ..database import UserManager

@post("/v1/images/generations", guards=[auth_guard, ratelimit_guard])
async def images(request: Request, data: ImageBody) -> PrettyJSONResponse:
    """Image endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)

    if not (await UserManager.get_property(key, "premium")) and data.model in AIModel.get_premium_models("images.generations"):
        return InvalidRequestException("This model is not available in the free tier.", status_code=402).to_response()

    return await (AIModel.get_random_provider(data.model))(data.model_dump())