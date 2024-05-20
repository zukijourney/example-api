from litestar import Request
from ..typings import ImageBody, ChatBody, AdminBody

endpoint_classes = {
    "/v1/images/generations": ImageBody,
    "/v1/chat/completions": ChatBody,
    "/admin": AdminBody
}

async def body_validator(request: Request):
    """Validates the request body"""
    body = await request.json()
    endpoint_classes[request.url.path](**body).validate()