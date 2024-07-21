import litestar
from litestar.config.cors import CORSConfig
from .helpers import load_routers
from .responses import PrettyJSONResponse
from .errors import get_exception_handlers

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