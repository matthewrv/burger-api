import uuid

from pydantic import BaseModel, Field

from app import security
from app.di import SessionDep
from db.user import User

from ..router import api_router


class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str = Field(max_length=30, min_length=8)


class RegisterUserResponse(BaseModel):
    name: str
    email: str


@api_router.post("/auth/register", response_model=RegisterUserResponse)
async def register_user(user: RegisterUserRequest, db: SessionDep):
    db_user = User(
        id=uuid.uuid4(),
        name=user.name,
        email=user.email,
        password_hash=security.get_password_hash(user.password),
    )

    with db.begin():
        db.add(db_user)

    return db_user
