from starlette.routing import Route
from .admin import admin
from .chat import chat
from .home import home
from .images import images
from .models import models

routes = [
    Route("/", endpoint=home),
    Route("/v1/models", endpoint=models),
    Route("/v1/chat/completions", endpoint=chat, methods=["POST"]),
    Route("/v1/images/generations", endpoint=images, methods=["POST"]),
    Route("/admin", endpoint=admin, methods=["POST"])
]