from dataclasses import dataclass
from typing import get_origin, get_args
from collections.abc import Iterable

@dataclass
class ChatBody:
    """
    The default body of chat requests
    """

    model: str
    messages: list
    stream: bool = False
    temperature: float | int = 1
    top_p: float | int = 1
    presence_penalty: float | int = 0
    frequency_penalty: float | int = 0

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