from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from api.auth.models import AuthResponse
from app import security
from app.db import SessionDep
from db.user import User

from ..router import api_router


class LoginRequst(BaseModel):
    email: str
    password: str


@api_router.post("/auth/login")
async def login(request: LoginRequst, db: SessionDep) -> AuthResponse:
    with db.begin():
        user = db.exec(select(User).where(User.email == request.email)).first()

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

    token = security.create_access_token(user)
    return AuthResponse(
        user=user.model_dump(), accessToken=f"Bearer {token}", refreshToken=token
    )
