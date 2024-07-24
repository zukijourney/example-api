import litestar
from ..models import Admin
from ...config import settings
from ...responses import PrettyJSONResponse
from ...db import UserManager

@litestar.post("/v1/admin/{action:str}", include_in_schema=False)
async def admin(request: litestar.Request, data: Admin, action: str) -> dict[str, str]:
    """The admin endpoint for the API."""

    received_admin_key = request.headers.get("Authorization", "").replace("Bearer ", "")

    if received_admin_key != settings.admin_key:
        return PrettyJSONResponse({"error": "Unauthorized"}, status_code=401)

    if action == "create":
        result = await UserManager.create_user(user=data.name)
    elif action == "update":
        result = await UserManager.update_user(
            property="name",
            value=data.name,
            data=data.user_info.model_dump(mode="json")
        )

    if action == "create":
        return {"message": "Successfully created the user.", "result": result.model_dump(mode="json")}
    else:
        return {"message": "Successfully updated the user.", "result": result.model_dump(mode="json")}