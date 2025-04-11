from pydantic import BaseModel

from ...router import api_router


class GetUserResponse(BaseModel):
    name: str
    email: str


@api_router.get("/auth/user", response_model=GetUserResponse)
async def get_user():
    return {"name": "test_user", "email": "test@example.com"}
