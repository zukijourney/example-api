import litestar
import typing
from ..provider_utils import get_all_models

@litestar.get("/v1/models", status_code=200)
async def models() -> typing.Dict[str, typing.Union[str, list]]:
    """The models endpoint for the API."""
    return {
        "object": "list",
        "data": get_all_models(formatted=True)
    }