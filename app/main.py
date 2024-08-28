import litestar
import asyncio
from litestar.config.cors import CORSConfig
from litestar.middleware.rate_limit import RateLimitConfig
from .responses import JSONResponse
from .tasks import add_credits_daily
from .endpoints import ROUTERS
from .errors import get_exception_handlers

def create_app() -> litestar.Litestar:
    """Create the Litestar app."""

    rate_limit_middleware = RateLimitConfig(rate_limit=("minute", 30), exclude_opt_key="exclude")

    def start_tasks() -> None:
        asyncio.create_task(add_credits_daily())

    return litestar.Litestar(
        route_handlers=ROUTERS,
        cors_config=CORSConfig(),
        response_class=JSONResponse,
        exception_handlers=get_exception_handlers(),
        middleware=[rate_limit_middleware.middleware],
        on_startup=[start_tasks]
    )

app = create_app()