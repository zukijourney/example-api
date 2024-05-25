from typing import Union, Iterable, Any
from pydantic import BaseModel, field_validator
from ..utils import AIModel

class EmbeddingBody(BaseModel):
    """
    The default body of embedding requests
    """

    model: str
    input: Union[str, list[str], Iterable[int], Iterable[Iterable[int]]]

    @field_validator("model")
    def validate_model(cls, v: str) -> Any:
        """Checks if a model is valid"""
        if v not in AIModel.get_all_models("embeddings"):
            raise ValueError(f"Invalid model: {v}")
        return v
    
    @classmethod
    def check_model(cls, model: str) -> None:
        """Triggers the Pydantic validator"""
        return cls.validate_model(model)