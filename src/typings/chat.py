from typing import Union, Literal, Optional, Any
from pydantic import BaseModel, field_validator
from ..utils import AIModel

class ChatBody(BaseModel):
    """
    The default body of chat requests
    """

    model: str
    messages: list[dict[str, Union[str, list]]]
    stream: bool = False
    temperature: Union[float, int] = 1
    top_p: Union[float, int] = 1
    presence_penalty: Union[float, int] = 0
    frequency_penalty: Union[float, int] = 0
    tools: Optional[list] = None
    tool_choice: Optional[Union[Literal["auto", "required", "none"], dict]] = None

    @field_validator("model")
    def validate_model(cls, v: str) -> Any:
        """Checks if a model is valid"""
        if v not in AIModel.get_all_models():
            raise ValueError(f"Invalid model: {v}")
        return v
    
    @classmethod
    def check_model(cls, model: str) -> None:
        """Triggers the Pydantic validator"""
        return cls.validate_model(model)