from starlette.requests import Request
from ..responses import PrettyJSONResponse
from ..utils.models import AIModel

async def models(_: Request):
    """Models endpoint request handler"""
    return PrettyJSONResponse(AIModel.all_to_json())