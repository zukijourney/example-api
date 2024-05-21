import ujson
from litestar.connection import ASGIConnection
from litestar.handlers.base import BaseRouteHandler
from litestar.exceptions import HTTPException
from asyncio_redis_rate_limit import RateLimiter, RateSpec, RateLimitError
from aioredis import Redis
from ..database import UserManager

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

redis = Redis.from_url(config["redisURI"])

rate_spec_map = {
    "normal": RateSpec(requests=5, seconds=60),
    "premium": RateSpec(requests=10, seconds=60),
}

async def ratelimit_guard(connection: ASGIConnection, _: BaseRouteHandler):
    """Rate limiting guard (executes before the route handler)"""

    key = connection.headers.get("Authorization", "").replace("Bearer ", "", 1)
    premium = await UserManager.get_property(key, "premium")

    try:
        async with RateLimiter(unique_key=key, backend=redis, rate_spec=rate_spec_map["premium" if premium else "normal"], cache_prefix="s"):
            pass
    except RateLimitError:
        raise HTTPException("Rate limit exceeded.", status_code=429)