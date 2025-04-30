from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware import cors
from sqlmodel import SQLModel

from api import api_router
from db.db import connect_to_db

from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = connect_to_db()
    async with engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        cors.CORSMiddleware,
        allow_origins=settings.allow_origins or (),
        allow_headers="*",
        allow_methods="*",
    )
    app.include_router(api_router)

    return app
