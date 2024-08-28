from .home import home
from .models import models
from .chat import chat_completion
from .embeddings import embeddings
from .images import image
from .audio import speech, transcription

ROUTERS = [
    home,
    models,
    chat_completion,
    embeddings,
    image,
    speech,
    transcription
]