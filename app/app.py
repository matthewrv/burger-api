from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast

import aio_pika
from fastapi import FastAPI
from fastapi.middleware import cors
from sqlmodel import SQLModel

from .api import api_router
from .config import settings
from .db import connect_to_db
from .use_cases import order_notifications


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    db_engine = connect_to_db()
    app.state.db = db_engine
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    rabbit_connection = cast(
        aio_pika.Connection, await aio_pika.connect(settings.rabbitmq_url)
    )
    app.state.rabbitmq = rabbit_connection

    async with order_notifications.lifespan(app, rabbit_connection):
        yield

    await rabbit_connection.close()
    await db_engine.dispose()


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
