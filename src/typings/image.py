from typing import Any
from pydantic import BaseModel, field_validator
from ..utils import AIModel

class ImageBody(BaseModel):
    """
    The default body of image requests
    """

    model: str
    prompt: str
    size: str = "1024x1024"

    @field_validator("model")
    def validate_model(cls, v: str) -> Any:
        if v not in AIModel.get_all_models("images.generations"):
            raise ValueError(f"Invalid model: {v}")
        return v

    @classmethod
    def check_model(cls, model: str) -> None:
        return cls.validate_model(model)