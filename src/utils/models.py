from dataclasses import dataclass, field
from ..providers import OpenAI
import random

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
    providers: list = field(default_factory=list)

    def to_json(self, full: bool = True):
        """Returns a JSON representation of the available AI models (and providers if specified)"""
        model_object = self.__dict__.copy()
        del model_object["providers"]
        return {"object": "model", "data": model_object} if full else model_object

    @classmethod
    def all_to_json(cls):
        """Returns a JSON representation of the list of available AI models"""
        return {"object": "list", "data": [model.to_json(full=False) for model in AIModels.models.values()]}

    @classmethod
    def get_all_models(cls):
        """Returns a list of all available AI models IDs"""
        return [model for model in cls.all_to_json()["data"]]

    @classmethod
    def get_provider_for_model(cls, model: str):
        """Returns a random provider for the given AI model"""
        return random.choice(AIModels.models.get(model).providers)

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

    gpt_4_o = AIModel(
        id="gpt-4o",
        providers=[OpenAI.chat]
    )
    gpt_4_turbo = AIModel(
        id="gpt-4-turbo",
        providers=[OpenAI.chat]
    )
    gpt_4_turbo_preview = AIModel(
        id="gpt-4-turbo-preview",
        providers=[OpenAI.chat]
    )
    gpt_4_1106_preview = AIModel(
        id="gpt-4-1106-preview",
        providers=[OpenAI.chat]
    )
    gpt_4 = AIModel(
        id="gpt-4",
        providers=[OpenAI.chat]
    )
    gpt_35_turbo_0125 = AIModel(
        id="gpt-3.5-turbo-0125",
        providers=[OpenAI.chat]
    )
    gpt_35_turbo_1106 = AIModel(
        id="gpt-3.5-turbo-1106",
        providers=[OpenAI.chat]
    )
    gpt_35_turbo = AIModel(
        id="gpt-3.5-turbo",
        providers=[OpenAI.chat]
    )
    dalle_3 = AIModel(
        id="dall-e-3",
        providers=[OpenAI.image],
        type="images.generations"
    )