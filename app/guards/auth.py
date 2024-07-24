import typing
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from ..db import UserManager
from ..responses import PrettyJSONResponse

async def auth_guard(connection: ASGIConnection, _: BaseRouteHandler) -> typing.Optional[PrettyJSONResponse]:
    """Checks if the user is authenticated."""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "")

    if key == "":
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": "You didn't provide an API key (e.g. Authorization: Bearer sk-...).",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=401
        )

    user = await UserManager.get_user(property="key", value=key)

    if not user:
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": "Invalid API key.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=401
        )
    elif user.banned:
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": "Your account has been banned.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=403
        )