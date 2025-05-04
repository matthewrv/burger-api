import uuid
from datetime import datetime, timezone

from pydantic import UUID4


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
