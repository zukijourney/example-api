import pydantic
import typing
from ..utils import get_all_models
from ...responses import PrettyJSONResponse

class Image(pydantic.BaseModel):
    """
    Represents the default image payload format for the API.
    """

    model: str
    prompt: str
    n: int = 1
    size: typing.Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "1024x1024"
    
    @pydantic.field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> typing.Union[str, PrettyJSONResponse]:
        if value not in get_all_models(type="images.generations"):
            return PrettyJSONResponse(
                content={
                    "error": {
                        "message": f"Model '{value}' not found.",
                        "type": "invalid_request_error",
                        "param": "model",
                        "code": None
                    }
                },
                status_code=404
            )
        return value