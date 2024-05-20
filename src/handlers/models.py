from litestar import get
from ..responses import PrettyJSONResponse
from ..utils.models import AIModel

@get("/v1/models")
async def models() -> PrettyJSONResponse:
    """Models endpoint request handler"""
    return PrettyJSONResponse(AIModel.all_to_json())