from dataclasses import dataclass, field
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
    providers: list = field(default_factory=list)
    _provider_index: int = field(default=0, init=False, repr=False)

    def to_json(self, full: bool = True):
        """Returns a JSON representation of an AI model (and its provider if specified)"""
        model_object = self.__dict__.copy()
        del model_object["providers"]
        return model_object if not full else self.__dict__.copy()

    @classmethod
    def all_to_json(cls):
        """Returns a JSON representation of the list of available AI models"""
        return {"object": "list", "data": [model.to_json(False) for model in AIModels.models.values()]}

    @classmethod
    def get_all_models(cls, type: str = "chat.completions", premium: bool = False):
        """Returns a list of all available AI models IDs"""
        return [model["id"] for model in cls.all_to_json()["data"] if model["type"] == type and model["premium"] == premium]

    @classmethod
    def get_random_provider(cls, model: str):
        """Returns a provider for the given AI model using round-robin load balancing"""
        ai_model = AIModels.models[model]
        provider = ai_model.providers[ai_model._provider_index]
        ai_model._provider_index = (ai_model._provider_index + 1) % len(ai_model.providers)
        return provider

class AIModelMeta(type):
    """
    Metaclass for the AIModel class
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.models = {value.id: value for value in attrs.values() if isinstance(value, AIModel)}

class AIModels(metaclass=AIModelMeta):
    """
    Class for registering AI models
    """

    model_data = [
        ("gpt-4o", "model", 0, "openai", "chat.completions", True, [OpenAI.chat_completion]),
        ("gpt-4-turbo", "model", 0, "openai", "chat.completions", True, [OpenAI.chat_completion]),
        ("gpt-4-turbo-preview", "model", 0, "openai", "chat.completions", True, [OpenAI.chat_completion]),
        ("gpt-4-1106-preview", "model", 0, "openai", "chat.completions", True, [OpenAI.chat_completion]),
        ("gpt-4", "model", 0, "openai", "chat.completions", False, [OpenAI.chat_completion]),
        ("gpt-3.5-turbo-0125", "model", 0, "openai", "chat.completions", False, [OpenAI.chat_completion]),
        ("gpt-3.5-turbo-1106", "model", 0, "openai", "chat.completions", False, [OpenAI.chat_completion]),
        ("gpt-3.5-turbo", "model", 0, "openai", "chat.completions", False, [OpenAI.chat_completion]),
        ("dall-e-3", "model", 0, "openai", "images.generations", True, [OpenAI.image])
    ]

    for model_id, *args in model_data:
        locals()[model_id.replace("-", "_")] = AIModel(model_id, *args)