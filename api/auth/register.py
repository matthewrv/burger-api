import uuid

from pydantic import BaseModel, Field

from api.auth.models import AuthResponse
from app import security
from app.db import SessionDep
from db.user import User

from ..router import api_router


class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str = Field(max_length=30, min_length=8)


@api_router.post("/auth/register")
async def register_user(user: RegisterUserRequest, db: SessionDep) -> AuthResponse:
    db_user = User(
        id=uuid.uuid4(),
        name=user.name,
        email=user.email,
        password_hash=security.get_password_hash(user.password),
    )

    with db.begin():
        db.add(db_user)

    token = security.create_access_token(db_user)
    return AuthResponse(
        user=db_user.model_dump(), accessToken=f"Bearer {token}", refreshToken=token
    )
