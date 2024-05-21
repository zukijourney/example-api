import ujson
from litestar import Request, post
from ..responses import PrettyJSONResponse
from ..typings import AdminBody
from ..database import UserManager
from ..utils import body_validator

with open("values/config.json", "r") as f:
    config = ujson.load(f)

@post("/admin", before_request=body_validator)
async def admin(request: Request, data: AdminBody) -> PrettyJSONResponse:
    """Admin endpoint request handler"""

    authorization = request.headers.get("Authorization")

    if authorization.replace("Bearer ", "", 1) != config["adminKey"]:
        return PrettyJSONResponse(
            content={"error": "Invalid admin key.", "success": False},
            status_code=401
        )
    elif data.action not in ["create", "get"]:
        return PrettyJSONResponse(
            content={"error": "Invalid action.", "success": False},
            status_code=404
        )

    if data.action == "create":
        if (await UserManager.get_user_by_id(data.id)):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key already exists."},
                status_code=400
            )
    elif data.action == "get":
        if not (await UserManager.get_user_by_id(data.id)):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key doesn't exist."},
                status_code=404
            )

    action_map = {
        "create": lambda: UserManager.create_key(data.id),
        "get": lambda: UserManager.get_user_by_id(data.id)
    }

    return PrettyJSONResponse({"success": True, "value": await action_map[data.action]()}, status_code=200)