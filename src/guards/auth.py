from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from ..database import UserManager
from ..exceptions import InvalidRequestException

async def auth_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Authentication guard (executes before the route handler)"""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "", 1)

    if key == "":
        raise InvalidRequestException("Missing authorization header.", status=401)
    elif not (await UserManager.check_key(key)):
        raise InvalidRequestException("Your key is invalid.", status=401)
    elif (await UserManager.get_property(key, "banned")):
        raise InvalidRequestException("Your key is banned.", status=401)