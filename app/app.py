from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import cors
from sqlmodel import SQLModel

from api import api_router

from .config import settings
from .db import connect_to_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = connect_to_db()
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_headers="*",
    allow_methods="*",
)
app.include_router(api_router)
