import typing
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from redis.asyncio import Redis
from asyncio_redis_rate_limit import RateLimiter, RateSpec, RateLimitError
from ..settings import settings
from ..database import UserManager
from ..responses import PrettyJSONResponse

redis = Redis.from_url(settings.redis_uri)

async def rate_limit_guard(connection: ASGIConnection, _: BaseRouteHandler) -> typing.Optional[PrettyJSONResponse]:
    """Checks if the user is rate limited."""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user(property="key", value=key)

    try:
        async with RateLimiter(unique_key=key, backend=redis, rate_spec=RateSpec(10 if user.premium else 3, 60), cache_prefix="s"):
            pass
    except RateLimitError:
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