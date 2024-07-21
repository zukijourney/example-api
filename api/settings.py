import os
import pydantic_settings

class Settings(pydantic_settings.BaseSettings):
    """
    Settings for the application. Used for loading environment variables.
    """

    admin_key: str
    redis_uri: str

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "secrets", ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
settings = Settings()