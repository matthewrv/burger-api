from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from db.user import User
from tests.conftest import SampleUser


def test_register(client: TestClient, session: Session, sample_user_data: SampleUser):
    with session.begin():
        session.exec(delete(User))
        result = session.exec(select(User)).all()
        assert len(result) == 0, f"Expected no users in db, but got {len(result)}"

    response = client.post(
        "/api/auth/register",
        json={
            "name": sample_user_data.name,
            "email": sample_user_data.email,
            "password": sample_user_data.password,
        },
    )
    assert response.status_code == 200

    with session.begin():
        users = session.exec(select(User)).all()

        assert len(users) == 1

        user = users[0]
        assert user.email == sample_user_data.email
        assert user.name == sample_user_data.name
