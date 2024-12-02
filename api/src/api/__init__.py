from fastapi import APIRouter
from .exceptions import (
    ValidationError,
    AuthenticationError,
    AccessError
)
from .routes import (
    home_router,
    models_router,
    chat_router,
    image_router,
    embeddings_router,
    moderations_router,
    audio_router
)

class RouterManager:
    def __init__(self):
        self.main_router = APIRouter()
        self.routers = [
            home_router,
            models_router,
            chat_router,
            image_router,
            embeddings_router,
            moderations_router,
            audio_router
        ]

    def setup_routes(self) -> APIRouter:
        for router in self.routers:
            self.main_router.include_router(router)
        return self.main_router

router_manager = RouterManager()
main_router = router_manager.setup_routes()

__all__ = [
    'main_router',
    'ValidationError',
    'AuthenticationError',
    'AccessError'
]