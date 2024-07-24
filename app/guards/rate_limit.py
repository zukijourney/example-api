import typing
import pyrate_limiter
import asyncer
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from ..db import UserManager
from ..responses import PrettyJSONResponse

limiter = pyrate_limiter.Limiter(pyrate_limiter.Rate(3, 1000))
premium_limiter = pyrate_limiter.Limiter(pyrate_limiter.Rate(10, 1000))

async def rate_limit_guard(connection: ASGIConnection, _: BaseRouteHandler) -> typing.Optional[PrettyJSONResponse]:
    """Checks if the user is rate limited."""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user(property="key", value=key)

    try:
        if user.premium:
            await asyncer.asyncify(premium_limiter.try_acquire)(key)
        else:
            await asyncer.asyncify(limiter.try_acquire)(key)
    except pyrate_limiter.BucketFullException:
        return PrettyJSONResponse(
            content={
                "error": {
                    "message": "Rate limit exceeded.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=429
        )