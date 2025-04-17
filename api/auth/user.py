from pydantic import BaseModel

from app import security

from .models import User
from .router import auth_router

__all__ = ("GetUserResponse", "get_user")


class GetUserResponse(BaseModel):
    user: User


@auth_router.get("/user")
async def get_user(user: security.UserDep) -> GetUserResponse:
    return GetUserResponse(user=User.model_validate(user, from_attributes=True))
