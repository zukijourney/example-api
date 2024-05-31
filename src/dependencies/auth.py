from fastapi import Request
from ..database import UserManager
from ..exceptions import InvalidRequestException

async def auth(request: Request) -> None:
    """Authentication dependency (executes before the route handler)"""

    key = request.headers.get("Authorization", "").replace("Bearer ", "", 1)

    if key == "":
        raise InvalidRequestException("Missing authorization header.", status=401)
    elif not (await UserManager.check_key(key)):
        raise InvalidRequestException("Your key is invalid.", status=401)
    
    check_ban = await UserManager.get_property(key, "banned")

    if check_ban:
        raise InvalidRequestException("Your key is banned.", status=401)