from litestar import post
from litestar.response import Stream
from typing import Union
from ..utils import AIModel, body_validator
from ..typings import ChatBody
from ..guards import auth_guard, ratelimit_guard
from ..responses import PrettyJSONResponse

@post("/v1/chat/completions", guards=[auth_guard, ratelimit_guard], before_request=body_validator)
async def chat(data: ChatBody) -> Union[Stream, PrettyJSONResponse]:
    """Chat endpoint request handler"""
    return await (AIModel.get_random_provider(data.model))(data.__dict__.copy())