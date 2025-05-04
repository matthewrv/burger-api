from fastapi import HTTPException, status
from pydantic import BaseModel

from app import security
from app.repo.user import UserRepoDep

from .models import AuthResponse, User
from .router import auth_router

__all__ = ("LoginRequest", "login", "AuthResponse")


class LoginRequest(BaseModel):
    email: str
    password: str


@auth_router.post("/login")
async def login(request: LoginRequest, user_repo: UserRepoDep) -> AuthResponse:
    user = await user_repo.get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    if not security.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    access_token, refresh_token = await user_repo.rotate_user_tokens(user)

    return AuthResponse(
        success=True,
        user=User.model_validate(user, from_attributes=True),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
