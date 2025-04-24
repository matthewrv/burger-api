from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlmodel import col, select

from app import security
from db.user import User
from db.utils import utc_now

from .base_repo import BaseRepo, as_transaction


class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None


class EmailAlreadyExists(Exception):
    pass


class UserRepo(BaseRepo):
    @as_transaction
    def update_user(self, user: User, update_user: UpdateUserRequest) -> User:
        # validate
        if update_user.email:
            another_user = self.get_user_by_email(update_user.email)
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
    def get_user_by_email(self, email: str) -> User | None:
        return self._session.exec(
            select(User).where(col(User.email) == email)
        ).one_or_none()


UserRepoDep = Annotated[UserRepo, Depends(UserRepo)]
