from typing import Literal, Any
from pydantic import BaseModel, field_validator
from ..utils import AIModel

class TTSBody(BaseModel):
    """
    The default body of TTS requests
    """

    model: str
    input: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    @field_validator("model")
    def validate_model(cls, v: str) -> Any:
        if v not in AIModel.get_all_models("tts"):
            raise ValueError(f"Invalid model: {v}")
        return v
    
    @classmethod
    def check_model(cls, model: str) -> None:
        return cls.validate_model(model)