from starlette.requests import Request
from ..exceptions import InvalidRequestException
from ..utils import AIModel

all_models = [model["id"] for model in AIModel.get_all_models() if model["type"] == "images.generations"]

async def images(request: Request):
    """Image endpoint request handler"""

    body = await request.json()

    if body.get("model") not in all_models:
        return InvalidRequestException(
            message=f"Model {body.get('model')} not found.",
            status=404
        ).to_response()

    return await (AIModel.get_provider_for_model(body.get("model")))(body)