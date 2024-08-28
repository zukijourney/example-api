import odmantic
import typing
from odmantic.bson import BaseBSONModel

class Model(BaseBSONModel):
    """
    Represents the model section in the provider document schema format.
    """

    api_name: str
    provider_name: str
    usage: int
    failures: int
    avg_latency: float
    last_failure: float

class Provider(odmantic.Model):
    """
    Represents the provider document schema format in the database.
    """

    name: str
    api_key: str
    api_url: str
    models: typing.List[Model]
    premium_only: bool

    model_config = {
        "collection": "providers"
    }