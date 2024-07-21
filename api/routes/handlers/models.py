import litestar
import typing
from ..utils import get_all_models

@litestar.get(["/v1/models", "/models"])
async def models() -> dict[str, typing.Union[str, typing.List[str]]]:
    """The models endpoint for the API."""
    return {
        "object": "list",
        "data": get_all_models(formatted=True)
    }