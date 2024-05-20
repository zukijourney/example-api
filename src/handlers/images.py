from litestar import post
from ..exceptions import InvalidRequestException
from ..guards import auth_guard
from ..typings import ImageBody
from ..utils import AIModel, body_validator
from ..responses import PrettyJSONResponse

all_models = [model["id"] for model in AIModel.get_all_models() if model["type"] == "images.generations"]

@post("/v1/images/generations", guards=[auth_guard], before_request=body_validator)
async def images(data: ImageBody) -> PrettyJSONResponse:
    """Image endpoint request handler"""

    if data.model not in all_models:
        return InvalidRequestException(
            message=f"Model {data.model} not found.",
            status=404
        ).to_response()

    return await (AIModel.get_random_provider(data.model))(data.__dict__.copy())