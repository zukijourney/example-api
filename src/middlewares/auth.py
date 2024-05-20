from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from ..storage import UserManager
from ..utils import InvalidRequestException

endpoints = [
    "/v1/chat/completions",
    "/v1/images/generations"
]

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.url.path in endpoints and request.method == "POST":
            key = request.headers.get("Authorization")

            if not key:
                return InvalidRequestException("Missing authorization header.", status=401).to_response()
                    
            key_check = await UserManager.check_key(key.replace("Bearer ", ""))

            if key_check is None:
                return InvalidRequestException("Your key is invalid.", status=401).to_response()

        return await call_next(request)