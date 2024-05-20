import ujson
from starlette.requests import Request
from ..responses import PrettyJSONResponse
from ..storage import UserManager

with open("values/config.json", "r") as f:
    config = ujson.load(f)

async def admin(request: Request):
    """Admin endpoint request handler"""

    body = await request.json()
    authorization = request.headers.get("Authorization")
    action, id = body.get("action"), body.get("id")

    if authorization.replace("Bearer ", "") != config["adminKey"]:
        return PrettyJSONResponse(
            content={"error": "Invalid admin key.", "success": False},
            status_code=401
        )
    elif action not in ["create", "get"]:
        return PrettyJSONResponse(
            content={"error": "Invalid action.", "success": False},
            status_code=404
        )

    if action == "create":
        if (await UserManager.get_user_by_id(id)):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key already exists."},
                status_code=400
            )
    elif action == "get":
        if not (await UserManager.get_user_by_id(id)):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key doesn't exist."},
                status_code=404
            )

    action_map = {
        "create": lambda: UserManager.create_key(id),
        "get": lambda: UserManager.get_user_by_id(id)
    }

    return PrettyJSONResponse({"success": True, "value": await action_map[body.get("action")]()})