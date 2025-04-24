from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allow_origins: list[str] | None = None
    port: int | None = 8000
    db_connection: str = "sqlite://"
    secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        enable_decoding=True,
    )

    @field_validator('allow_origins', mode="before")
    @classmethod
    def get_allowed_origins(cls, value: str) -> list[str]:
        if not value:
            return []
        return value.split(',')

settings = Settings()
