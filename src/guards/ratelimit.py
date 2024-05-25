import ujson
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from asyncio_redis_rate_limit import RateLimiter, RateSpec, RateLimitError
from aioredis import Redis
from ..database import UserManager
from ..exceptions import InvalidRequestException

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

redis = Redis.from_url(config["redisURI"])

async def ratelimit_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Rate limiting guard (executes before the route handler)"""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "", 1)
    premium = await UserManager.get_property(key, "premium")

    try:
        async with RateLimiter(unique_key=key, backend=redis, rate_spec=RateSpec(10 if premium else 3, 60), cache_prefix="s"):
            pass
    except RateLimitError:
        raise InvalidRequestException("Rate limit exceeded.", status=429)