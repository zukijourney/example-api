import litestar
import time
from litestar.exceptions import HTTPException, ValidationException
from .model_utils import get_all_models
from ..database import UserManager

async def before_request(request: litestar.Request) -> None:
    """A hook that runs before the request is processed."""

    key = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await UserManager.get_user("key", key)

    if user.premium_tier > 0 and time.time() > user.premium_expiry:
        user.premium_tier = 0
        await UserManager.update_user(property="key", value=key, user=user.model_dump())

    body = await request.json()

    if not any(model["id"] == body.get("model") for model in get_all_models(type=request.url.path.replace("/v1/", "").replace("/", "."))):
        raise ValidationException(
            detail=f"The model '{body.get('model')}' does not exist.",
            extra=[{"key": "model"}]
        )
    
    if request.url.path == "/v1/audio/speech":
        if not any(body.get("voice") in model["voices"] for model in get_all_models(type="audio.speech")):
            raise ValidationException(
                detail=f"The voice '{body.get('voice')}' does not exist.",
                extra=[{"key": "voice"}]
            )

    is_premium_model = any(model["id"] == body.get("model") and model["premium_only"] for model in get_all_models())

    if is_premium_model and not user.premium_tier > 0:
        raise HTTPException(
            detail="You need to be a premium user to use this model.",
            extra={"code": "premium_required"},
            status_code=403
        )

    if user.premium_tier < 2:
        if not user.ip:
            user.ip = request.headers.get("X-Real-Ip")
            await UserManager.update_user(property="key", value=key, user=user.model_dump())
        elif user.ip != request.headers.get("X-Real-Ip"):
            raise HTTPException(
                detail="Your current IP address is different from the one in the database. Please reset your IP using '/key reset-ip' at: https://discord.gg/example",
                extra={"code": "ip_address_mismatch"},
                status_code=403
            )
    
    if body.get("model"):
        print(f"[{user.user_id}] Model: {body['model']}")