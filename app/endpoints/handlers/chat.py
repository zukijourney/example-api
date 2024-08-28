import litestar
import typing
import asyncer
from litestar.response import Stream
from ...database import UserManager
from ..provider_utils import get_provider_class
from ...responses import JSONResponse
from ..models import Chat
from ...hooks import before_request
from ...guards import auth_guard

@litestar.post("/v1/chat/completions", guards=[auth_guard], before_request=before_request, status_code=200)
async def chat_completion(request: litestar.Request, data: Chat) -> typing.Union[JSONResponse, Stream]:
    """The chat endpoint for the API."""

    provider = await asyncer.asyncify(get_provider_class)(data.model)

    key = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user("key", key)

    token_count = sum(
        round(len(content) / 4)
        if message.get("type") == "text" and isinstance(message["content"], list)
        else 250
        for message in data.messages
        for content in (message["content"] if isinstance(message["content"], list) else [message["content"]])
    )

    if token_count > user.credits:
        return JSONResponse(
            content={
                "error": {
                    "message": "This request would bring your credit count to below 0. Please use a smaller prompt or wait for a credit refill.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": None
                }
            },
            status_code=403
        )

    return await provider.chat_completion(data, key)