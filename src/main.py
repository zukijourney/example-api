from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from .utils import configure_error_handlers
from .handlers import routes
from .middlewares import configure_middlewares

app = Starlette(
    routes=routes,
    exception_handlers=configure_error_handlers(),
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_headers=["*"],
            allow_methods=["*"]
        )
    ]
)

configure_middlewares(app)