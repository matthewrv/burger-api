from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

__all__ = ("User", "AuthResponse")


class User(BaseModel):
    name: str
    email: str


class AuthResponse(BaseModel):
    success: bool
    user: User
    access_token: str
    refresh_token: str

    model_config = ConfigDict(alias_generator=to_camel)
