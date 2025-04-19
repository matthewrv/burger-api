from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import SessionDep
from db.user import User
from db.utils import utc_now

from .config import settings

# Parameters for JWT tokens
# to get a string for secret key run this command:
# openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_HOURS = 48

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        bytes(password, encoding="utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def raise_auth_exception():
    raise HTTPException(
        # FIXME 403 is for compatibility with old frontend version
        # need to update frontend and backend
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(user: User) -> str:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(user, expires_delta)


def create_refresh_token(user: User) -> str:
    expires_delta = timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    return create_token(user, expires_delta)


def create_token(user: User, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {"sub": user.email, "exp": now + expires_delta, "iat": now}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "sub"]},
        )
        email = payload.get("sub")
    except jwt.InvalidTokenError:
        raise_auth_exception()

    with db.begin():
        user = db.exec(select(User).where(User.email == email)).first()

    if user is None or user.refresh_token_hash is None:
        raise_auth_exception()

    issued_at = datetime.fromtimestamp(payload.get("iat"), timezone.utc).replace(
        tzinfo=None
    )
    if issued_at and user.logout_at and issued_at < user.logout_at:
        raise_auth_exception()

    return user


class RequestWithRefreshToken(BaseModel):
    token: str


async def validate_refresh_token(
    db: SessionDep, request: RequestWithRefreshToken
) -> User:
    db_user = await get_current_user(db, request.token)
    is_valid_refresh_token = verify_password(request.token, db_user.refresh_token_hash)

    if not is_valid_refresh_token:
        raise_auth_exception()

    return db_user


UserDep = Annotated[User, Depends(get_current_user)]
UserByRefreshTokenDep = Annotated[User, Depends(validate_refresh_token)]


def rotate_user_tokens(db: Session, user: User):
    # remove microseconds since we do not store them in JWT
    now = utc_now().replace(microsecond=0)
    refresh_token = create_refresh_token(user)
    access_token = create_access_token(user)

    with db.begin():
        user.logout_at = now
        user.refresh_token_hash = get_password_hash(refresh_token)

    return access_token, refresh_token
