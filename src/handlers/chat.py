from litestar import post
from litestar.response import Stream
from ..exceptions import InvalidRequestException
from ..utils import AIModel, body_validator
from ..typings import ChatBody
from ..guards import auth_guard
from ..responses import PrettyJSONResponse

all_models = [model["id"] for model in AIModel.get_all_models() if model["type"] == "chat.completions"]

@post("/v1/chat/completions", guards=[auth_guard], before_request=body_validator)
async def chat(data: ChatBody) -> Stream | PrettyJSONResponse:
    """Chat endpoint request handler"""

    if data.model not in all_models:
        return InvalidRequestException(
            message=f"Model {data.model} not found.",
            status=404
        ).to_response()

    return await (AIModel.get_random_provider(data.model))(data.__dict__.copy())