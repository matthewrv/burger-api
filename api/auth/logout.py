from pydantic import BaseModel

from app.repo.user import UserRepoDep
from app.security import UserByRefreshTokenDep

from .router import auth_router


class LogoutRequest(BaseModel):
    token: str


class LogoutResponse(BaseModel):
    success: bool


@auth_router.post("/logout")
async def logout(user: UserByRefreshTokenDep, user_repo: UserRepoDep) -> LogoutResponse:
    await user_repo.logout_user(user)
    return LogoutResponse(success=True)
