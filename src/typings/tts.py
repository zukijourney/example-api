from typing import Literal
from dataclasses import dataclass

@dataclass
class TTSBody:
    """
    The default body of TTS requests
    """

    model: str
    input: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]