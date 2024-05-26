from litestar import Litestar
from litestar.config.cors import CORSConfig
from .utils import configure_error_handlers
from .handlers import routes

app = Litestar(
    route_handlers=routes,
    exception_handlers=configure_error_handlers(),
    cors_config=CORSConfig(max_age=3600)
)