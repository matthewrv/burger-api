from functools import lru_cache
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

__all__ = ("SessionDep", "EngineDep")


@lru_cache
def connect_to_db() -> AsyncEngine:
    return create_async_engine(settings.db_connection)


async def get_db_engine() -> AsyncEngine:
    return connect_to_db()


EngineDep = Annotated[AsyncEngine, Depends(get_db_engine)]


async def get_session(
    engine: EngineDep,
) -> AsyncGenerator[AsyncSession]:
    # give developer full control over transactions - this is how it should be
    async with AsyncSession(engine, expire_on_commit=False, autobegin=False) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
