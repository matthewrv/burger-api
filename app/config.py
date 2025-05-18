from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allow_origins: list[str] | None = None
    port: int = 8000
    db_connection: str = "sqlite://"
    secret_key: str
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    rabbitmq_url: str | None = None
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        enable_decoding=True,
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def get_allowed_origins(cls, value: str) -> list[str]:
        if not value:
            return []
        return value.split(",")


settings = Settings()
