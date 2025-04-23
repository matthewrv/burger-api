from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allow_origins: list[str] | None
    port: int | None = 8000
    db_connection: str = "sqlite://"
    secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        enable_decoding=True,
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def decode_allow_origins(cls, v: str | None) -> list[str]:
        if not v:
            return []
        return v.split(",")


settings = Settings()
