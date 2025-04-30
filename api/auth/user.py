from fastapi import HTTPException
from pydantic import BaseModel

from app import security
from app.repo.user import EmailAlreadyExists, UpdateUserRequest, UserRepoDep

from .models import User
from .router import auth_router

__all__ = ("GetUserResponse", "get_user", "patch_user")


class GetUserResponse(BaseModel):
    user: User


class PatchUserResponse(BaseModel):
    success: bool
    user: User


@auth_router.get("/user")
async def get_user(user: security.UserDep) -> GetUserResponse:
    return GetUserResponse(user=User.model_validate(user, from_attributes=True))


@auth_router.patch("/user")
async def patch_user(
    user: security.UserDep,
    update_user_request: UpdateUserRequest,
    user_repo: UserRepoDep,
) -> PatchUserResponse:
    try:
        user = await user_repo.update_user(user, update_user_request)
        return PatchUserResponse(
            success=True, user=User.model_validate(user, from_attributes=True)
        )
    except EmailAlreadyExists:
        raise HTTPException(
            400, {"success": False, "message": "Email already reserved"}
        )
