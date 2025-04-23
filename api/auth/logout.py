from pydantic import BaseModel

from app.db import SessionDep
from app.security import UserByRefreshTokenDep
from db.utils import utc_now

from .router import auth_router


class LogoutRequest(BaseModel):
    token: str


class LogoutResponse(BaseModel):
    success: bool


@auth_router.post("/logout")
async def logout(db_user: UserByRefreshTokenDep, db: SessionDep) -> LogoutResponse:
    with db.begin():
        db_user.refresh_token_hash = None
        db_user.logout_at = utc_now()

    return LogoutResponse(success=True)
