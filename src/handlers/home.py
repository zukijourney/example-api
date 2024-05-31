from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter()

@router.get("/", response_model=None)
async def home() -> ORJSONResponse:
    """Home endpoint request handler"""
    return ORJSONResponse({
        "message": "Welcome to my very own self-hosted AI reverse proxy!",
        "github": "https://github.com/zukijourney/example-api",
    })