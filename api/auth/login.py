from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app import security
from db.db import SessionDep
from db.user import User as DbUser

from .models import AuthResponse, User
from .router import auth_router

__all__ = ("LoginRequest", "login", "AuthResponse")


class LoginRequest(BaseModel):
    email: str
    password: str


@auth_router.post("/login")
async def login(request: LoginRequest, db: SessionDep) -> AuthResponse:
    with db.begin():
        user = db.exec(select(DbUser).where(DbUser.email == request.email)).first()

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

    access_token, refresh_token = security.rotate_user_tokens(db, user)

    return AuthResponse(
        success=True,
        user=User.model_validate(user, from_attributes=True),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
