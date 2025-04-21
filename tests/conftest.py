import datetime
import unittest.mock
import uuid
from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app import db, security
from app.app import create_app
from db.ingredient import Ingredient
from db.user import User


@pytest.fixture(name="app")
def get_test_app() -> Generator[FastAPI]:
    @lru_cache
    def connect_to_db() -> Engine:
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(engine)
        return engine

    app = create_app()
    app.dependency_overrides[db.connect_to_db] = connect_to_db

    yield app

    app.dependency_overrides.clear()


@pytest.fixture(name="session")
def get_session(app: FastAPI) -> Generator[Session, None, None]:
    session_context = contextmanager(db.get_session)
    engine = app.dependency_overrides[db.connect_to_db]()
    with session_context(engine) as session:
        yield session


@pytest.fixture(name="client")
def get_client(app: FastAPI, session: Session) -> Generator[TestClient, None, None]:
    yield TestClient(app)


class SampleUser(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    password: str
    refresh_token: str


@pytest.fixture(name="sample_user_data")
def get_sample_user_data() -> SampleUser:
    test_user = SampleUser(
        id=uuid.UUID("0f854aa6-30d9-4525-806f-aad3cdaa2e18"),
        name="test",
        email="test@example.com",
        password="12345678",
        refresh_token="placeholder",
    )
    test_user.refresh_token = security.create_refresh_token(test_user)
    return test_user


@pytest.fixture(name="test_user")
def add_test_user(session: Session, sample_user_data: SampleUser) -> SampleUser:
    with session.begin():
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


@pytest.fixture(name="ingredients")
def add_test_ingredients(session: Session) -> list[Ingredient]:
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
    with session.begin():
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
        with unittest.mock.patch("db.utils._utc_now", return_value=now) as mock:
            yield mock
    else:
        yield None
