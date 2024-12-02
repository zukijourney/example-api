from .models import router as models_router
from .chat_completions import router as chat_router
from .images_generations import router as image_router
from .embeddings import router as embeddings_router
from .moderations import router as moderations_router
from .audio import router as audio_router

__all__ = [
    'models_router',
    'chat_router',
    'image_router',
    'embeddings_router',
    'moderations_router',
    'audio_router'
]