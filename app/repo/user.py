import uuid
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlmodel import col, select

from app import security
from db.tables.user import User
from db.utils import utc_now

from .base_repo import BaseRepo, as_transaction


class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str


class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None


class EmailAlreadyExists(Exception):
    pass


class UserRepo(BaseRepo):
    @as_transaction
    async def update_user(self, user: User, update_user: UpdateUserRequest) -> User:
        # validate
        if update_user.email:
            another_user = await self.get_user_by_email(update_user.email)
            if another_user:
                raise EmailAlreadyExists()

        # update
        login_info_changed = False

        if update_user.name:
            user.name = update_user.name

        if update_user.email:
            user.email = update_user.email
            login_info_changed = True

        if update_user.password:
            user.password_hash = security.get_password_hash(update_user.password)
            login_info_changed = True

        if login_info_changed:
            user.refresh_token_hash = None
            user.logout_at = utc_now()

        return user

    @as_transaction
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self._session.exec(select(User).where(col(User.email) == email))
        return result.one_or_none()

    @as_transaction
    async def rotate_user_tokens(self, user: User) -> tuple[str, str]:
        # remove microseconds since we do not store them in JWT
        now = utc_now().replace(microsecond=0)
        refresh_token = security.create_refresh_token(user)
        access_token = security.create_access_token(user)

        user.logout_at = now
        user.refresh_token_hash = security.get_password_hash(refresh_token)

        return access_token, refresh_token

    @as_transaction
    async def logout_user(self, user: User) -> None:
        user.refresh_token_hash = None
        user.logout_at = utc_now()

    @as_transaction
    async def create_user(self, request: CreateUserRequest) -> tuple[User, str, str]:
        db_user = User(
            id=uuid.uuid4(),
            name=request.name,
            email=request.email,
            password_hash=security.get_password_hash(request.password),
            refresh_token_hash="",
        )
        access_token = security.create_access_token(db_user)
        refresh_token = security.create_refresh_token(db_user)
        db_user.refresh_token_hash = security.get_password_hash(refresh_token)

        self._session.add(db_user)

        return db_user, access_token, refresh_token


UserRepoDep = Annotated[UserRepo, Depends(UserRepo)]
