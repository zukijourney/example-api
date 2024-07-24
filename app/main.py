import litestar
import os
import importlib
import typing
from litestar.handlers.http_handlers import HTTPRouteHandler
from litestar.config.cors import CORSConfig
from .db import init_db
from .responses import PrettyJSONResponse
from .errors import get_exception_handlers

def load_routers() -> typing.Set[HTTPRouteHandler]:
    """Loads routers dynamically from the routers directory and returns them."""

    routers = set()
    handlers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "routes", "handlers"))

    for root, _, files in os.walk(handlers_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))[:-3].replace(os.path.sep, ".")
                module = importlib.import_module(f"app.{module_name}")
                for obj in module.__dict__.values():
                    if isinstance(obj, HTTPRouteHandler):
                        routers.add(obj)

    return routers

app = litestar.Litestar(
    route_handlers=list(load_routers()),
    cors_config=CORSConfig(),
    response_class=PrettyJSONResponse,
    exception_handlers=get_exception_handlers(),
    on_startup=[init_db]
)