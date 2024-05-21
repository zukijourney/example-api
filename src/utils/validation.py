from litestar import Request
from typing import Union
from .errors import InvalidRequestException
from .models import AIModel
from ..database import UserManager
from ..typings import ImageBody, ChatBody, AdminBody
from ..responses import PrettyJSONResponse

endpoint_classes = {
    "/v1/images/generations": ImageBody,
    "/v1/chat/completions": ChatBody,
    "/admin": AdminBody
}

async def body_validator(request: Request) -> Union[None, PrettyJSONResponse]:
    """Request body validator (before request hook)"""

    body = await request.json()
    key = request.headers.get("Authorization", "").replace("Bearer ", "", 1)

    endpoint_classes[request.url.path](**body).validate()

    if request.url.path == "/admin":
        if body.get("action") not in ["create", "get", "update", "delete"]:
            return InvalidRequestException(message=f"Invalid action: {body.get('action')}", status=404).to_response()
        if body.get("action") == "update" and not all([body.get("status"), body.get("property")]):
            return InvalidRequestException(message="Missing status or property", status=400).to_response()
        if body.get("action") == "get" and body.get("property") not in ["premium", "banned"]:
            return InvalidRequestException(message="Invalid property", status=400).to_response()
    else:
        model_type = request.url.path.replace("/v1/", "").replace("/", ".")
        if body.get("model") not in (AIModel.get_all_models(model_type, True) + AIModel.get_all_models(model_type, False)):
            return InvalidRequestException(message=f"Model {body.get('model')} not found.", status=404).to_response()
        if not await UserManager.get_property(key, "premium") and body.get("model") in AIModel.get_all_models(model_type, True):
            return InvalidRequestException(message="This model is not available in the free plan.", status=403).to_response()