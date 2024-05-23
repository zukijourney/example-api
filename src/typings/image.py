from dataclasses import dataclass

@dataclass
class ImageBody:
    """
    The default body of image requests
    """

    model: str
    prompt: str
    size: str = "1024x1024"