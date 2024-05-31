from .admin import router as admin
from .chat import router as chat
from .home import router as home
from .images import router as images
from .models import router as models
from .embeddings import router as embedding
from .moderation import router as moderation
from .tts import router as tts

routes = [
    admin,
    chat,
    home,
    images,
    models,
    embedding,
    moderation,
    tts
]