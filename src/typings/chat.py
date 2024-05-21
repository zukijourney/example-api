from typing import Union, get_args, get_origin
from dataclasses import dataclass
from collections.abc import Iterable

@dataclass
class ChatBody:
    """
    The default body of chat requests
    """

    model: str
    messages: list
    stream: bool = False
    temperature: Union[float, int] = 1
    top_p: Union[float, int] = 1
    presence_penalty: Union[float, int] = 0
    frequency_penalty: Union[float, int] = 0

    def validate(self):
        """Validates the body"""
        for field_name, field_type in self.__annotations__.items():
            value = getattr(self, field_name)
            origin = get_origin(field_type)
            args = get_args(field_type)
            
            if origin is Union:
                if not any(isinstance(value, arg) for arg in args):
                    raise ValueError(f"{field_name} must be one of {args}")
            elif isinstance(value, Iterable) and origin:
                if not all(isinstance(item, args[0]) for item in value):
                    raise ValueError(f"All items in {field_name} must be of type {args[0]}")
            elif not isinstance(value, field_type):
                raise ValueError(f"{field_name} must be of type {field_type}")