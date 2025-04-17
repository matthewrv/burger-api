from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .config import settings

__all__ = "SessionDep"


@lru_cache
def connect_to_db() -> Engine:
    return create_engine(
        settings.db_connection, connect_args={"check_same_thread": False}
    )


def get_session(engine: Annotated[Engine, Depends(connect_to_db)]):
    # give developer full control over transactions - this is how it should be
    with Session(engine, expire_on_commit=False, autobegin=False) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
