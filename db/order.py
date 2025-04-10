import datetime

from pydantic import UUID4
from sqlmodel import UUID, Field, SQLModel


class Order(SQLModel, table=True):
    id: UUID4 = Field(UUID(as_uuid=True), primary_key=True)
    created_at: datetime.datetime = Field(index=True)
    name: str = Field(max_length=255)
    number: int
