import litestar
import typing
from .utils import get_all_models
from ..db import UserManager
from ..responses import PrettyJSONResponse

async def before_request(request: litestar.Request) -> typing.Optional[PrettyJSONResponse]:
    """A hook that runs before the request is processed."""

    key = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user("key", key)
    body = await request.json()

    if user:
        if any(model["id"] == body.get("model", "") and model["premium"] for model in get_all_models()):
            if not user.premium:
                return PrettyJSONResponse(
                    content={
                        "error": {
                            "message": "You need to be a premium user to use this model.",
                            "type": "invalid_request_error",
                            "param": None,
                            "code": None
                        }
                    },
                    status_code=403
                )