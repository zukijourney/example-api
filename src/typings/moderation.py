from typing import Union, Any
from pydantic import BaseModel, field_validator
from ..utils import AIModel

class ModerationBody(BaseModel):
    """
    The default body of moderation requests
    """

    model: str
    input: Union[str, list[str]]

    @field_validator("model")
    def validate_model(cls, v: str) -> Any:
        if v not in AIModel.get_all_models("moderation"):
            raise ValueError(f"Invalid model: {v}")
        return v

    @classmethod
    def check_model(cls, model: str) -> None:
        return cls.validate_model(model)