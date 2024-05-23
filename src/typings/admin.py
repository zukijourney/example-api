from typing import Optional, Any
from pydantic import BaseModel, field_validator

class AdminBody(BaseModel):
    """
    The default body of admin requests
    """

    id: int
    action: str
    status: Optional[bool] = None
    property: Optional[str] = None

    @field_validator("action")
    def validate_action(cls, v: str) -> Any:
        if v not in ["create", "get", "update", "delete"]:
            raise ValueError(f"Invalid action: {v}")
        return v
    
    @classmethod
    def check_action(cls, action: str) -> None:
        return cls.validate_action(action)