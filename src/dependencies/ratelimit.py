import ujson
from fastapi import Request
from redis.asyncio import Redis
from asyncio_redis_rate_limit import RateLimiter, RateSpec, RateLimitError
from ..database import UserManager
from ..exceptions import InvalidRequestException

with open("values/secrets.json") as f:
    config = ujson.load(f)

redis = Redis.from_url(config["redisURI"])

async def rate_limit(request: Request) -> None:
    """Rate limiting dependency (executes before the route handler)"""

    key = request.headers.get("Authorization", "").replace("Bearer ", "", 1)
    premium = await UserManager.get_property(key, "premium")

    try:
        async with RateLimiter(unique_key=key, backend=redis, rate_spec=RateSpec(10 if premium else 3, 60), cache_prefix="s"):
            pass
    except RateLimitError:
        raise InvalidRequestException("Rate limit exceeded.", status=429)