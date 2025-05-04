from pydantic import BaseModel, Field

__all__ = ("User", "AuthResponse")


class User(BaseModel):
    name: str
    email: str


class AuthResponse(BaseModel):
    success: bool
    user: User
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
