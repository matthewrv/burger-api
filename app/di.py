from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .config import settings


@lru_cache
def connect_to_db() -> Engine:
    return create_engine(
        settings.db_connection, connect_args={"check_same_thread": False}
    )


def get_session(engine: Annotated[Engine, Depends(connect_to_db)]):
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]
