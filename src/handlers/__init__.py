from .admin import admin
from .chat import chat
from .home import home
from .images import images
from .models import models
from .embeddings import embedding
from .moderation import moderation
from .tts import tts

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