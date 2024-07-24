import litestar
import typing
import asyncer
from litestar.response import Stream
from ..utils import get_provider_class
from ...responses import PrettyJSONResponse
from ..models import Image
from ...hooks import before_request
from ...guards import auth_guard, rate_limit_guard

@litestar.post(["/v1/images/generations", "/images/generations"], guards=[auth_guard, rate_limit_guard], before_request=before_request)
async def chat(data: Image) -> typing.Union[PrettyJSONResponse, Stream]:
    """The image endpoint for the API."""
    provider = await asyncer.asyncify(get_provider_class)(data.model)
    return await provider.image_generation(data)