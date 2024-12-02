from .home import router as home_router
from .v1 import (
    models_router,
    chat_router,
    image_router,
    embeddings_router,
    moderations_router,
    audio_router
)

__all__ = [
    'home_router',
    'models_router',
    'chat_router',
    'image_router',
    'embeddings_router',
    'moderations_router',
    'audio_router'
]