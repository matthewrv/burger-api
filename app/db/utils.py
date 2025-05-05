import uuid
from datetime import datetime, timezone

from pydantic import UUID4
from sqlalchemy import DateTime, Dialect
from sqlalchemy.types import TypeDecorator


class TZDateTime(TypeDecorator[datetime]):
    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: None | datetime, dialect: Dialect
    ) -> None | datetime:
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(
        self, value: None | datetime, dialect: Dialect
    ) -> None | datetime:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value


def utc_now() -> datetime:
    """datetime gen for SQLAlchemy default fields."""
    return _utc_now()


def _utc_now() -> datetime:
    """This function is mocked in tests."""
    return datetime.now(timezone.utc)


def random_uuid() -> UUID4:
    """
    UUID4 gen for SQLAlchemy default fields.

    Required to mock uuid generation during tests.
    """
    return uuid.uuid4()
