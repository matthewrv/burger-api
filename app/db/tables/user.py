from datetime import datetime

from pydantic import UUID4
from sqlmodel import UUID, Field, SQLModel

from app.db.utils import TZDateTime, utc_now


class User(SQLModel, table=True):
    id: UUID4 = Field(UUID(as_uuid=True), primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str
    created_at: datetime = Field(default_factory=utc_now, sa_type=TZDateTime)
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=TZDateTime,
        sa_column_kwargs={"onupdate": utc_now},
    )
    refresh_token_hash: str | None
    logout_at: datetime | None = Field(None, sa_type=TZDateTime)

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.name}, email={self.email})"
