from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from ..utils.models import AIModel

router = APIRouter()

@router.get("/v1/models", response_model=None)
async def models() -> ORJSONResponse:
    """Models endpoint request handler"""
    return ORJSONResponse(AIModel.all_to_json())