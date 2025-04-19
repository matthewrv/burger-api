from datetime import datetime

from pydantic import UUID4
from sqlmodel import UUID, Field, SQLModel

from .utils import utc_now


class User(SQLModel, table=True):
    id: UUID4 = Field(UUID(as_uuid=True), primary_key=True)
    name: str = Field()
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column_kwargs={"onupdate": utc_now}
    )
    refresh_token_hash: str | None = None
    logout_at: datetime | None = None

    def __repr__(self):
        return f"User(id={self.id}, username={self.name}, email={self.email})"
