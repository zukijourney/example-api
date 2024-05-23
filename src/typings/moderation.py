from dataclasses import dataclass
from typing import Union

@dataclass
class ModerationBody:
    """
    The default body of moderation requests
    """

    model: str
    input: Union[str, list[str]]