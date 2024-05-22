from litestar import post
from ..guards import auth_guard, ratelimit_guard
from ..typings import EmbeddingBody
from ..utils import AIModel, body_validator
from ..responses import PrettyJSONResponse

@post("/v1/embeddings", guards=[auth_guard, ratelimit_guard], before_request=body_validator)
async def embedding(data: EmbeddingBody) -> PrettyJSONResponse:
    """Embedding endpoint request handler"""
    return await (AIModel.get_random_provider(data.model))(data.__dict__.copy())