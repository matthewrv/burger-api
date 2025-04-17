import uuid

from pydantic import BaseModel
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


@pytest.fixture(name="test_user")
def add_test_user(session: Session):
    test_user = SampleUser(
        id=uuid.UUID("0f854aa6-30d9-4525-806f-aad3cdaa2e18"),
        name = "test",
        email = "test@example.com",
        password = "12345678",
    )

    with session.begin():
        db_user = User(
            id=test_user.id,
            name=test_user.name,
            email=test_user.email,
            password_hash=security.get_password_hash(test_user.password),
        )

        session.add(db_user)

    yield test_user
