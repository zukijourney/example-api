from dataclasses import dataclass
from typing import Optional, get_origin, get_args
from collections.abc import Iterable

@dataclass
class AdminBody:
    """
    The default body of admin requests
    """

    id: int
    action: str
    status: Optional[bool] = None

    def validate(self):
        for field_name, field_type in self.__annotations__.items():
            value = getattr(self, field_name)
            origin = get_origin(field_type)
            args = get_args(field_type)
            
            if origin and isinstance(value, Iterable):
                if not all(isinstance(item, args[0]) for item in value):
                    raise ValueError(f"{field_name} must be of type {field_type}")
            elif not isinstance(value, field_type):
                raise ValueError(f"{field_name} must be of type {field_type}")