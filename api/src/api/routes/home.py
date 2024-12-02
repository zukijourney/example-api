from fastapi import APIRouter
from typing import Dict
from ...responses import JSONResponse

router = APIRouter()

@router.get('/', response_class=JSONResponse)
async def home() -> Dict[str, str]:
    return {
        'message': 'Welcome to an instance of the Zukijourney Example API! The source code is available at: https://github.com/zukijourney/example-api'
    }