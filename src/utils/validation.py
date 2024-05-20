from litestar import Request
from ..typings import ImageBody, ChatBody, AdminBody

typing_map = {
    "/v1/images/generations": ImageBody,
    "/v1/chat/completions": ChatBody,
    "/admin": AdminBody
}

async def body_validator(request: Request):
    """Validates the request body"""
    body = await request.json()
    typing_map[request.url.path](**body).validate()