from typing import Union, Iterable
from dataclasses import dataclass

@dataclass
class EmbeddingBody:
    """
    The default body of embedding requests
    """

    model: str
    input: Union[str, list[str], Iterable[int], Iterable[Iterable[int]]]