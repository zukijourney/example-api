from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from litestar.exceptions import HTTPException
from ..database import UserManager

async def auth_guard(connection: ASGIConnection, _: BaseRouteHandler):
    """Authentication guard (executes before the route handler)"""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "", 1)

    if key == "":
        raise HTTPException("Missing authorization header.", status_code=401)
    elif not (await UserManager.check_key(key)):
        raise HTTPException("Your key is invalid.", status_code=401)
    elif (await UserManager.get_property(key, "banned")):
        raise HTTPException("Your key is banned.", status_code=401)