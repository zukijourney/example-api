import odmantic
import typing

class User(odmantic.Model):
    """
    Represents the user document schema format in the database.
    """    

    user_id: int
    key: str
    premium_tier: int
    premium_expiry: float
    banned: bool
    credits: float
    last_daily: float
    ip: typing.Optional[str]

    model_config = {
        "collection": "users"
    }