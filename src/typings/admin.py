from typing import Optional
from dataclasses import dataclass

@dataclass
class AdminBody:
    """
    The default body of admin requests
    """

    id: int
    action: str
    status: Optional[bool] = None
    property: Optional[str] = None