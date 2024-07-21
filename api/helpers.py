import os
import importlib
from litestar.handlers.http_handlers import HTTPRouteHandler

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