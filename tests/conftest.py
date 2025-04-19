import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app import db, security
from app.app import app
from db.user import User


@pytest.fixture(name="session")
def get_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False, autobegin=False) as session:
        yield session


@pytest.fixture(name="client")
def get_client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[db.get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class SampleUser(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    password: str
    refresh_token: str


@pytest.fixture(name="sample_user_data")
def get_sample_user_data():
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
def add_test_user(session: Session, sample_user_data: SampleUser):
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

    yield sample_user_data
