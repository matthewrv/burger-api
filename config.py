from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    allow_origins: list[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        enable_decoding=False,
        extra="ignore",
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def decode_allow_origins(cls, v: str) -> list[int]:
        return [x for x in v.split(",")]


settings = Settings()
