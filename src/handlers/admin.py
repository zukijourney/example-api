import ujson
from ..responses import PrettyJSONResponse
from starlette.requests import Request
from ..storage import UserManager

with open("values/config.json", "r") as f:
    config = ujson.load(f)

async def admin(request: Request):
    """Admin endpoint request handler"""

    body = await request.json()
    authorization = request.headers.get("Authorization")

    if authorization.replace("Bearer ", "") != config["adminKey"]:
        return PrettyJSONResponse(
            content={"error": "Invalid admin key.", "success": False},
            status_code=401
        )
    elif body.get("action") not in ["create", "get"]:
        return PrettyJSONResponse(
            content={"error": "Invalid action.", "success": False},
            status_code=404
        )

    if body.get("action") == "create":
        if (await UserManager.get_user_by_id(body.get("id"))):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key already exists."},
                status_code=400
            )
    else:
        if not (await UserManager.get_user_by_id(body.get("id"))):
            return PrettyJSONResponse(
                content={"success": False, "value": "Key doesn't exist."},
                status_code=404
            )

    action_map = {
        "create": lambda: UserManager.create_key(body.get("id")),
        "get": lambda: UserManager.get_user_by_id(body.get("id"))
    }

    return PrettyJSONResponse({"success": True, "value": await action_map[body.get("action")]()})