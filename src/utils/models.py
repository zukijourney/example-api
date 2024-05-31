from dataclasses import dataclass, field
from typing import Union
from collections.abc import Callable
from ..providers import OpenAI

@dataclass
class AIModel:
    """
    Dataclass for handling AI model-related data
    """

    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "openai"
    type: str = "chat.completions"
    premium: bool = False
    endpoint: str = "/v1/chat/completions"
    providers: list = field(default_factory=list)
    _provider_index: int = field(default=0, init=False, repr=False)

    def to_json(self, full: bool = True) -> dict[str, Union[str, int, list, bool]]:
        """Returns a JSON representation of an AI model (and its provider if specified)"""
        model_object = self.__dict__.copy()
        del model_object["providers"]
        return model_object if not full else self.__dict__.copy()

    @classmethod
    def all_to_json(cls) -> dict[str, Union[str, int, bool]]:
        """Returns a JSON representation of the list of available AI models"""
        return {"object": "list", "data": [model.to_json(False) for model in AIModels.models.values()]}

    @classmethod
    def get_all_models(cls, type: str = "chat.completions") -> list[str]:
        """Returns a list of all available AI models IDs"""
        return [model["id"] for model in cls.all_to_json()["data"] if model["type"] == type]
    
    @classmethod
    def get_premium_models(cls, type: str = "chat.completions") -> list[str]:
        """Returns a list of all available premium AI models IDs"""
        return [model["id"] for model in cls.all_to_json()["data"] if model["type"] == type and model["premium"] == True]

    @classmethod
    def get_provider(cls, model: str) -> Callable:
        """Returns a provider for the given AI model using round-robin load balancing"""
        ai_model = AIModels.models[model]
        provider = ai_model.providers[ai_model._provider_index]
        ai_model._provider_index = (ai_model._provider_index + 1) % len(ai_model.providers)
        return provider

class AIModelMeta(type):
    """
    Metaclass for the AIModel class that initializes and registers AI models
    """

    def __init__(cls, name, bases, attrs) -> None:
        super().__init__(name, bases, attrs)
        cls.models = {value.id: value for value in attrs.values() if isinstance(value, AIModel)}

class AIModels(metaclass=AIModelMeta):
    """
    Class for registering and managing AI models.
    """

    gpt_3_5_turbo = AIModel(
        id="gpt-3.5-turbo",
        providers=[OpenAI.chat_completion]
    )
    gpt_3_5_turbo_1106 = AIModel(
        id="gpt-3.5-turbo-1106",
        providers=[OpenAI.chat_completion]
    )
    gpt_3_5_turbo_0125 = AIModel(
        id="gpt-3.5-turbo-0125",
        providers=[OpenAI.chat_completion]
    )
    gpt_4 = AIModel(
        id="gpt-4",
        providers=[OpenAI.chat_completion]
    )
    gpt_4_1106_preview = AIModel(
        id="gpt-4-1106-preview",
        premium=True,
        providers=[OpenAI.chat_completion]
    )
    gpt_4_turbo_preview = AIModel(
        id="gpt-4-turbo-preview",
        premium=True,
        providers=[OpenAI.chat_completion]
    )
    gpt_4_turbo = AIModel(
        id="gpt-4-turbo",
        premium=True,
        providers=[OpenAI.chat_completion]
    )
    gpt_4o = AIModel(
        id="gpt-4o",
        premium=True,
        providers=[OpenAI.chat_completion]
    )
    dall_e_3 = AIModel(
        id="dall-e-3",
        type="images.generations",
        premium=True,
        providers=[OpenAI.image],
        endpoint="/v1/images/generations"
    )
    text_moderation_latest = AIModel(
        id="text-moderation-latest",
        type="moderations",
        providers=[OpenAI.moderation],
        endpoint="/v1/moderations"
    )
    text_moderation_stable = AIModel(
        id="text-moderation-stable",
        type="moderations",
        providers=[OpenAI.moderation],
        endpoint="/v1/moderations"
    )
    text_embedding_3_small = AIModel(
        id="text-embedding-3-small",
        type="embeddings",
        providers=[OpenAI.embedding],
        endpoint="/v1/embeddings"
    )
    text_embedding_3_large = AIModel(
        id="text-embedding-3-large",
        type="embeddings",
        premium=True,
        providers=[OpenAI.embedding],
        endpoint="/v1/embeddings"
    )
    tts_1 = AIModel(
        id="tts-1",
        type="audio.speech",
        providers=[OpenAI.tts],
        endpoint="/v1/audio/speech"
    )
    tts_1_hd = AIModel(
        id="tts-1-hd",
        type="audio.speech",
        premium=True,
        providers=[OpenAI.tts],
        endpoint="/v1/audio/speech"
    )