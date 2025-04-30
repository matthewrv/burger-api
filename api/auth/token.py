from app.repo.user import UserRepoDep
from app.security import UserByRefreshTokenDep

from .models import AuthResponse, User
from .router import auth_router


@auth_router.post("/token")
async def update_access_token(
    user: UserByRefreshTokenDep, user_repo: UserRepoDep
) -> AuthResponse:
    access_token, refresh_token = await user_repo.rotate_user_tokens(user)

    return AuthResponse(
        success=True,
        user=User.model_validate(user, from_attributes=True),
        accessToken=f"Bearer {access_token}",
        refreshToken=refresh_token,
    )
