import uuid

from pydantic import BaseModel, Field

from app import security
from app.db import SessionDep
from db.user import User as DbUser

from .models import AuthResponse, User
from .router import auth_router

__all__ = ("RegisterUserRequest", "register_user", "AuthResponse")


class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str = Field(max_length=30, min_length=8)


@auth_router.post("/register")
async def register_user(user: RegisterUserRequest, db: SessionDep) -> AuthResponse:
    with db.begin():
        db_user = DbUser(
            id=uuid.uuid4(),
            name=user.name,
            email=user.email,
            password_hash=security.get_password_hash(user.password),
            refresh_token_hash="",
        )
        access_token = security.create_access_token(db_user)
        refresh_token = security.create_refresh_token(db_user)
        db_user.refresh_token_hash = security.get_password_hash(refresh_token)

        db.add(db_user)

    return AuthResponse(
        success=True,
        user=User.model_validate(user, from_attributes=True),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
