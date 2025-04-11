from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app import security
from app.di import SessionDep
from db.user import User

from ..router import api_router


class LoginRequst(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequst, db: SessionDep):
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

    token = "mock token"
    refresh_token = "mock refresh token"
    return {"access_token": f"Bearer {token}", "refresh_token": refresh_token}
