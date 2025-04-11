from datetime import datetime

from pydantic import UUID4
from sqlmodel import UUID, Field, SQLModel


class User(SQLModel, table=True):
    id: UUID4 = Field(UUID(as_uuid=True), primary_key=True)
    name: str = Field()
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"
