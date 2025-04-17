import datetime
import uuid

from pydantic import UUID4
from sqlmodel import Field, SQLModel

from .utils import utc_now


class Order(SQLModel, table=True):
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime.datetime = Field(index=True, default_factory=utc_now)
    updated_at: datetime.datetime = Field(
        index=True, default_factory=utc_now, sa_column_kwargs={"onupdate": utc_now}
    )
    name: str = Field(max_length=255)
    number: int
    owner_id: UUID4 = Field(foreign_key="user.id")
    status: str
