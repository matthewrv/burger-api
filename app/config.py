from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allow_origins: list[str] | None
    port: int | None
    db_connection: str
    secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        enable_decoding=True,
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def decode_allow_origins(cls, v: str) -> list[str] | None:
        if not v:
            return None
        return [x for x in v.split(",")]


settings = Settings()
