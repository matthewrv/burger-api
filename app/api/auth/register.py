from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.repo.user import CreateUserRequest, EmailAlreadyExists, UserRepoDep

from .models import AuthResponse, User
from .router import auth_router

__all__ = ("RegisterUserRequest", "register_user", "AuthResponse")


class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str = Field(max_length=30, min_length=8)


@auth_router.post("/register")
async def register_user(
    user: RegisterUserRequest, user_repo: UserRepoDep
) -> AuthResponse:
    try:
        db_user, access_token, refresh_token = await user_repo.create_user(
            CreateUserRequest.model_validate(user, from_attributes=True)
        )
    except EmailAlreadyExists as exc:
        raise HTTPException(400, detail=str(exc))

    return AuthResponse(
        success=True,
        user=User.model_validate(db_user, from_attributes=True),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
