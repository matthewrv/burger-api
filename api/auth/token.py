from app import security
from app.security import UserByRefreshTokenDep
from db.db import SessionDep

from .models import AuthResponse, User
from .router import auth_router


@auth_router.post("/token")
async def update_access_token(
    user: UserByRefreshTokenDep, db: SessionDep
) -> AuthResponse:
    access_token, refresh_token = security.rotate_user_tokens(db, user)

    return AuthResponse(
        success=True,
        user=User.model_validate(user, from_attributes=True),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
