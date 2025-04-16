import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine, text

from app import db, security
from app.app import app
from db.user import User


@pytest.fixture(name="session")
def get_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def get_client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[db.get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


TEST_USER_ID = uuid.UUID("0f854aa6-30d9-4525-806f-aad3cdaa2e18")
TEST_USER_PASSWORD = "12345678"


@pytest.fixture(name="test_user")
def add_test_user(session: Session):
    test_name = "test"
    test_email = "test@example.com"
    test_password = TEST_USER_PASSWORD

    test_user = User(
        id=TEST_USER_ID,
        name=test_name,
        email=test_email,
        password_hash=security.get_password_hash(test_password),
    )

    copy = test_user.model_copy()
    session.add(test_user)
    session.commit()
    yield copy
