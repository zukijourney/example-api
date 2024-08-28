import litestar
import asyncer
import typing
from litestar.params import Body
from ...database import UserManager
from ..provider_utils import get_provider_class
from ...responses import JSONResponse
from ..models import Speech, Transcription
from ...hooks import before_request
from ...guards import auth_guard

@litestar.post("/v1/audio/speech", guards=[auth_guard], before_request=before_request, status_code=200)
async def speech(request: litestar.Request, data: Speech) -> typing.Union[litestar.Response, JSONResponse]:
    """The speech endpoint for the API."""

    provider = await asyncer.asyncify(get_provider_class)(data.model)

    key = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user("key", key)
    model = next((model for model in provider.ai_models if model["id"] == data.model), None)

    if model:
        if model.get("cost", 100) + (len(data.input) / 4) > user.credits:
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

    return await provider.speech(data, key)

@litestar.post("/v1/audio/transcriptions", guards=[auth_guard], before_request=before_request, status_code=200)
async def transcription(request: litestar.Request, data: typing.Annotated[Transcription, Body(media_type="multipart/form-data")]) -> JSONResponse:
    """The transcription endpoint for the API."""

    provider = await asyncer.asyncify(get_provider_class)(data.model)

    key = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user("key", key)
    model = next((model for model in provider.ai_models if model["id"] == data.model), None)

    if model:
        if model.get("cost", 100) > user.credits:
            return JSONResponse(
                content={
                    "error": {
                        "message": "This request would bring your credit count to below 0. Please use a cheaper model or wait for a credit refill.",
                        "type": "invalid_request_error",
                        "param": None,
                        "code": None
                    }
                },
                status_code=403
            )

    return await provider.transcription(data, key)