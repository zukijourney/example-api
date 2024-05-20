from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from ..typings import ChatBody, ImageBody, AdminBody
from ..utils import InvalidRequestException

endpoint_map = {
    "/v1/chat/completions": ChatBody,
    "/v1/images/generations": ImageBody,
    "/admin": AdminBody
}

class ValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.url.path in endpoint_map.keys() and request.method == "POST":
            try:
                endpoint_map[request.url.path](**(await request.json())).validate()
            except Exception as e:
                return InvalidRequestException(f"Invalid request body ({str(e)}).", status=400).to_response()

        return await call_next(request)