from litestar import post, Request
from litestar.response import Stream
from typing import Union
from ..utils import AIModel, InvalidRequestException
from ..typings import ChatBody
from ..guards import auth_guard, ratelimit_guard
from ..responses import PrettyJSONResponse
from ..database import UserManager

@post("/v1/chat/completions", guards=[auth_guard, ratelimit_guard])
async def chat(request: Request, data: ChatBody) -> Union[Stream, PrettyJSONResponse]:
    """Chat endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)

    if not (await UserManager.get_property(key, "premium")) and data.model in AIModel.get_premium_models():
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_random_provider(data.model))(data.model_dump())