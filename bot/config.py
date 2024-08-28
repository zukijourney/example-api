import os
import typing
import pydantic
import pydantic_settings

class Settings(pydantic_settings.BaseSettings):
    """
    Settings for the application.
    Used for loading the .env config file.
    """

    token: str
    database_url: str
    database_name: str
    credits: pydantic.Json[typing.List[int]]

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")),
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()