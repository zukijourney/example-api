from litestar import get
from ..responses import PrettyJSONResponse

@get("/")
async def home() -> PrettyJSONResponse:
    """Home endpoint request handler"""
    return PrettyJSONResponse({"message": "Welcome to my very own self-hosted AI reverse proxy!"})