from app import security
from app.db import SessionDep
from app.security import UserByRefreshTokenDep

from .models import AuthResponse
from .router import auth_router


@auth_router.post("/token")
async def update_access_token(
    user: UserByRefreshTokenDep, db: SessionDep
) -> AuthResponse:
    access_token, refresh_token = security.rotate_user_tokens(db, user)

    return AuthResponse(
        success=True,
        user=user.model_dump(),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
