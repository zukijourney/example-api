from starlette.applications import Starlette
from .auth import AuthMiddleware
from .validation import ValidationMiddleware

def configure_middlewares(app: Starlette):
    app.add_middleware(ValidationMiddleware)
    app.add_middleware(AuthMiddleware)
    return