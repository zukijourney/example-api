from starlette.requests import Request
from ..responses import PrettyJSONResponse

async def home(_: Request):
    """Home endpoint request handler"""
    return PrettyJSONResponse({"message": "Welcome to the Zukijourney example API!"})