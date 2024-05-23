import ujson
from litestar import Request, post
from ..responses import PrettyJSONResponse
from ..typings import AdminBody
from ..database import UserManager

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

@post("/admin")
async def admin(request: Request, data: AdminBody) -> PrettyJSONResponse:
    """Admin endpoint request handler"""

    authorization = request.headers.get("Authorization")

    if authorization.replace("Bearer ", "", 1) != config["adminKey"]:
        return PrettyJSONResponse(
            content={"error": "Invalid admin key.", "success": False},
            status_code=401
        )

    if data.action == "create":
        if (await UserManager.get_user_by_id(data.id)):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key already exists."},
                status_code=400
            )
    elif data.action in ["get", "update", "delete"]:
        if not (await UserManager.get_user_by_id(data.id)):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key doesn't exist."},
                status_code=404
            )

    action_map = {
        "create": lambda: UserManager.create_key(data.id),
        "get": lambda: UserManager.get_user_by_id(data.id),
        "delete": lambda: UserManager.delete_key(data.id),
        "update": lambda: UserManager.set_property(data.id, data.property, data.status)
    }

    result = await action_map[data.action]()

    if data.action in ["get", "create"]:
        return PrettyJSONResponse({"success": True, "value": result}, status_code=200)
    else:
        return PrettyJSONResponse({"success": True, "message": "Successfully executed your action."}, status_code=200)