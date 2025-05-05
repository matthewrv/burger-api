from datetime import datetime

from pydantic import UUID4
from sqlmodel import Field, Identity, SQLModel

from app.db.utils import TZDateTime, random_uuid, utc_now


class Order(SQLModel, table=True):
    id: UUID4 = Field(default_factory=random_uuid, primary_key=True)
    created_at: datetime = Field(
        index=True, sa_type=TZDateTime, default_factory=utc_now
    )
    # This is actually not the best practice to update time from python.
    # Better to update time in database itself, but for my case this solution
    # is good enough
    updated_at: datetime = Field(
        index=True,
        default_factory=utc_now,
        sa_type=TZDateTime,
        sa_column_kwargs={"onupdate": utc_now},
    )
    name: str = Field(max_length=255)
    number: int = Field(
        sa_column_args=[Identity(always=True, start=1000, maxvalue=9999, cycle=True)]
    )
    owner_id: UUID4 = Field(foreign_key="user.id")
    status: str
