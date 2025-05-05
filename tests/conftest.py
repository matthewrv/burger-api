import datetime
import unittest.mock
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel, StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession

from app import security
from app.app import create_app
from app.db import Ingredient, User, db
from app.db.tables.order import Order
from app.db.tables.order_ingredient import OrderIngredient


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(name="app")
async def get_test_app() -> AsyncGenerator[FastAPI]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def get_test_db() -> AsyncEngine:
        return engine

    app = create_app()
    app.dependency_overrides[db.get_db_engine] = get_test_db

    yield app

    app.dependency_overrides.clear()


@pytest.fixture(name="session")
async def get_session(app: FastAPI) -> AsyncGenerator[AsyncSession]:
    session_context = asynccontextmanager(db.get_session)
    engine = await app.dependency_overrides[db.get_db_engine]()
    async with session_context(engine) as session:
        yield session


@pytest.fixture(name="client")
async def get_client(
    app: FastAPI, session: AsyncSession
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGIWebSocketTransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class SampleUser(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    password: str
    access_token: str
    refresh_token: str


@pytest.fixture(name="sample_user_data")
def get_sample_user_data() -> SampleUser:
    test_user = SampleUser(
        id=uuid.UUID("0f854aa6-30d9-4525-806f-aad3cdaa2e18"),
        name="test",
        email="test@example.com",
        password="12345678",
        access_token="placeholder",
        refresh_token="placeholder",
    )

    # set issue date 10 seconds earlier to test token invalidation without time.sleep
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=-10)
    test_user.access_token = security.create_access_token(test_user, now)
    test_user.refresh_token = security.create_refresh_token(test_user, now)
    return test_user


@pytest.fixture(name="test_user")
async def add_test_user(
    session: AsyncSession, sample_user_data: SampleUser
) -> SampleUser:
    async with session.begin():
        db_user = User(
            id=sample_user_data.id,
            name=sample_user_data.name,
            email=sample_user_data.email,
            password_hash=security.get_password_hash(sample_user_data.password),
            refresh_token_hash=security.get_password_hash(
                sample_user_data.refresh_token
            ),
        )

        session.add(db_user)

    return sample_user_data


@pytest.fixture(name="test_user_2")
async def add_test_user_2(session: AsyncSession) -> SampleUser:
    test_user_2 = SampleUser(
        id=uuid.UUID("0f854aa6-30d9-4525-806f-aad3cdaa2e19"),
        name="test_user_2",
        email="test2@example.com",
        password="12345678",
        access_token="placeholder",
        refresh_token="placeholder",
    )
    # set issue date 10 seconds earlier to test token invalidation without time.sleep
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=-10)
    test_user_2.access_token = security.create_access_token(test_user_2, now)
    test_user_2.refresh_token = security.create_refresh_token(test_user_2, now)

    async with session.begin():
        db_user = User(
            id=test_user_2.id,
            name=test_user_2.name,
            email=test_user_2.email,
            password_hash=security.get_password_hash(test_user_2.password),
            refresh_token_hash=security.get_password_hash(test_user_2.refresh_token),
        )

        session.add(db_user)

    return test_user_2


@pytest.fixture(name="ingredients")
async def add_test_ingredients(session: AsyncSession) -> list[Ingredient]:
    common_params = {
        "proteins": 100,
        "fat": 100,
        "carbohydrates": 100,
        "calories": 33,
        "price": 200,
        "image": "https://example.com/img.png",
        "image_large": "https://example.com/img.png",
        "image_mobile": "https://example.com/img.png",
        "burger_word": "тестовый",
    }
    async with session.begin():
        ingredients = [
            Ingredient.model_validate(
                {
                    "name": "Булка",
                    "type": "bun",
                    **common_params,
                }
            ),
            Ingredient.model_validate(
                {"name": "Соус", "type": "sauce", **common_params},
            ),
            Ingredient.model_validate(
                {"name": "Котлета", "type": "main", **common_params},
            ),
        ]
        session.add_all(ingredients)

    return ingredients


@pytest.fixture(name="order")
async def add_sample_order(
    session: AsyncSession, test_user: User, ingredients: list[Ingredient]
) -> Order:
    test_id = uuid.UUID("5296181d-ea21-4dfe-a8b5-c99561fc00f8")
    async with session.begin():
        order = Order(
            id=test_id,
            name="test order",
            number=1234,
            owner_id=test_user.id,
            status="pending",
        )
        order_ingredients = [
            OrderIngredient(order_id=order.id, ingredient_id=ingredient.id)
            for ingredient in ingredients
        ]
        session.add_all([order, *order_ingredients])

    return order


@pytest.fixture(autouse=True)
def mock_uuid_generation() -> Generator[
    unittest.mock.MagicMock | unittest.mock.AsyncMock
]:
    predefined_uuids = [
        uuid.UUID("2d75d3fa-bf09-450a-bcb6-5067648b01e8"),
        uuid.UUID("0c46c950-ef05-41a4-ba2b-d3224bfd4e2e"),
        uuid.UUID("f8ceba02-7bf4-484b-9df0-f527134fdc83"),
        uuid.UUID("da6d00b6-c692-4fa9-8624-479a13c30c7f"),
        uuid.UUID("e5853fe5-148e-4cde-bc63-2a9272d52884"),
        uuid.UUID("ca519bc6-87fb-461f-a959-d023c859aef5"),
        uuid.UUID("d20ed67c-f257-4ed5-a911-082529e0ca2a"),
        uuid.UUID("595fc04d-3e59-4470-ac16-5d0ca9ac6dbe"),
        uuid.UUID("d41f987d-5969-4129-b2a0-589236c2e9a4"),
        uuid.UUID("c870c128-5949-4f28-b00d-4a0aac87e184"),
    ]

    with unittest.mock.patch("uuid.uuid4", side_effect=predefined_uuids) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_utc_now(
    request: pytest.FixtureRequest,
) -> Generator[None | unittest.mock.MagicMock | unittest.mock.AsyncMock]:
    mark = request.node.get_closest_marker("now")
    if mark:
        value, *_ = mark.args
        now = datetime.datetime.fromisoformat(value)
        assert now.tzinfo is not None, "now mark must be timezone aware datetime"
        with unittest.mock.patch("app.db.utils._utc_now", return_value=now) as mock:
            yield mock
    else:
        yield None
