from litestar import post, Request
from ..guards import auth_guard, ratelimit_guard
from ..typings import EmbeddingBody
from ..utils import AIModel, InvalidRequestException
from ..responses import PrettyJSONResponse
from ..database import UserManager

@post("/v1/embeddings", guards=[auth_guard, ratelimit_guard])
async def embedding(request: Request, data: EmbeddingBody) -> PrettyJSONResponse:
    """Embedding endpoint request handler"""

    key = request.headers.get("Authorization").replace("Bearer ", "", 1)
    premium_check = await UserManager.get_property(key, "premium")
    is_premium_model = data.model in AIModel.get_premium_models("embeddings")

    if not premium_check and is_premium_model:
        raise InvalidRequestException("This model is not available in the free tier.", status_code=402)

    return await (AIModel.get_random_provider(data.model))(data.model_dump())