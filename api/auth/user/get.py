from pydantic import BaseModel

from app import security

from ...router import api_router
from ..models import User


class GetUserResponse(BaseModel):
    user: User


@api_router.get("/auth/user")
async def get_user(user: security.UserDep) -> GetUserResponse:
    return GetUserResponse(user=User.model_validate(user, from_attributes=True))
