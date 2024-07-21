import os
import importlib
import litestar
from litestar.handlers.http_handlers import HTTPRouteHandler
from litestar.config.cors import CORSConfig
from .responses import PrettyJSONResponse
from .errors import get_exception_handlers

def load_routers() -> set[HTTPRouteHandler]:
    """Loads routers dynamically from the routers directory and returns them."""

    routers = set()

    for _, _, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), "routes", "handlers"))):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"api.routes.handlers.{file[:-3]}")
                for _, obj in module.__dict__.items():
                    if isinstance(obj, HTTPRouteHandler):
                        routers.add(obj)
                   
    return routers

def create_app() -> litestar.Litestar:
    """Creates the main API application class."""

    routers = load_routers()

    return litestar.Litestar(
        route_handlers=list(routers),
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True
        ),
        response_class=PrettyJSONResponse,
        exception_handlers=get_exception_handlers()
    )

app = create_app()