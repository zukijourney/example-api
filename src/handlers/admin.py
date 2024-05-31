import ujson
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from ..typings import AdminBody
from ..database import UserManager

router = APIRouter()

with open("values/secrets.json", "r") as f:
    config = ujson.load(f)

@router.post("/admin", response_model=None)
async def admin(request: Request, data: AdminBody) -> ORJSONResponse:
    """Admin endpoint request handler"""

    authorization = request.headers.get("Authorization")

    if authorization.replace("Bearer ", "", 1) != config["adminKey"]:
        return ORJSONResponse(
            content={"error": "Invalid admin key.", "success": False},
            status_code=401
        )

    if data.action == "create":
        if (await UserManager.get_user_by_id(data.id)):
            return ORJSONResponse(
                content={"success": False, "value": "Key already exists."},
                status_code=400
            )
    elif data.action in ["get", "update", "delete"]:
        if not (await UserManager.get_user_by_id(data.id)):
            return ORJSONResponse(
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
        return ORJSONResponse({"success": True, "value": result})

    return ORJSONResponse({"success": True, "message": "Successfully executed your action."})