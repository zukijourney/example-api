from litestar.exceptions import HTTPException
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from ..database import UserManager

async def auth_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Check if the user is authenticated."""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "")

    if key == "":
        raise HTTPException(
            detail="You need to provide your API key in an Authorization header. Get your key at: https://discord.gg/example",
            extra={"code": "invalid_key"},
            status_code=401
        )

    user = await UserManager.get_user(property="key", value=key)

    if not user:
        raise HTTPException(
            detail="The provided key was not valid. Try again with another key or get one at: https://discord.gg/example",
            extra={"code": "invalid_key"},
            status_code=401
        )
    elif user.banned:
        raise HTTPException(
            detail="Your key is banned from using the API. Do you think we made a mistake? Appeal your punishment at: https://discord.gg/example",
            extra={"code": "banned_key"},
            status_code=403
        )