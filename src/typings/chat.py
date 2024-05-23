from typing import Union, Literal, Optional
from dataclasses import dataclass

@dataclass
class ChatBody:
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
    tool_choice: Union[Literal["auto", "required", "none"], dict] = "none"