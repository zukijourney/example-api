from typing import Union, Literal, Any, get_args, get_origin
from dataclasses import dataclass
from collections.abc import Iterable

@dataclass
class TTSBody:
    """
    The default body of TTS requests
    """

    model: str
    input: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"

    def validate(self) -> None:
        """Validates the body"""
        for field_name, field_type in self.__annotations__.items():
            value = getattr(self, field_name)
            origin = get_origin(field_type)
            args = get_args(field_type)

            if origin is Union:
                if not self.__validate_union__(value, args):
                    raise ValueError(f"{field_name} must be one of {args}")
            elif origin is Literal:
                if value not in args:
                    raise ValueError(f"{field_name} must be one of {args}")
            elif origin and issubclass(origin, Iterable) and not isinstance(value, str):
                if not all(self.__is_instance__(item, args[0]) for item in value):
                    raise ValueError(f"All items in {field_name} must be of type {args[0]}")
            else:
                if not self.__is_instance__(value, field_type):
                    raise ValueError(f"{field_name} must be of type {field_type}")

    def __validate_union__(self, value: Any, args: tuple[type]) -> bool:
        """Helper function to validate Union types"""
        return any(self.__is_instance__(value, arg) for arg in args)

    def __is_instance__(self, value: Any, field_type: type) -> bool:
        """Helper function to check instances, avoiding issues with subscripted generics."""
        origin = get_origin(field_type)
        if origin:
            if origin is Literal:
                return value in get_args(field_type)
            return isinstance(value, origin)
        return isinstance(value, field_type)