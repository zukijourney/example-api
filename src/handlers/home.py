from litestar import get
from ..responses import PrettyJSONResponse

@get("/")
async def home() -> PrettyJSONResponse:
    """Home endpoint request handler"""
    return PrettyJSONResponse({"message": "Welcome to the Zukijourney example API!"})