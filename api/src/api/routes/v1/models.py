from fastapi import APIRouter
from typing import Dict, Any
from ...utils import ModelListGenerator
from ....responses import JSONResponse

router = APIRouter()

@router.get('/v1/models', response_class=JSONResponse)
async def home() -> Dict[str, Any]:
    return {
        'object': 'list',
        'data': ModelListGenerator.generate()
    }