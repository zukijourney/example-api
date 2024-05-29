from litestar import post, Request
from litestar.response import Stream
from typing import Union
from ..utils import AIModel, InvalidRequestException
from ..typings import ChatBody
from ..guards import auth_guard, ratelimit_guard
from ..responses import PrettyJSONResponse
from ..database import UserManager

@post("/v1/chat/completions", guards=[auth_guard, ratelimit_guard], status_code=200)
async def chat(request: Request, data: ChatBody) -> Union[Stream, PrettyJSONResponse]:
    """Chat endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)
    premium_check = await UserManager.get_property(key, "premium")
    is_premium_model = data.model in AIModel.get_premium_models()

    if not premium_check and is_premium_model:
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_random_provider(data.model))(data.model_dump())