from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from db.user import User
from tests.conftest import SampleUser


def test_register(
    client: TestClient, session: Session, sample_user_data: SampleUser
) -> None:
    with session.begin():
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
    response_body = response.json()
    assert "accessToken" in response_body
    register_access_token = response_body["accessToken"]
    assert "refreshToken" in response_body

    with session.begin():
        users = session.exec(select(User)).all()

        assert len(users) == 1

        user = users[0]
        assert user.email == sample_user_data.email
        assert user.name == sample_user_data.name

    # assert register access token is valid
    response = client.get(
        "/api/auth/user", headers={"Authorization": register_access_token}
    )
    assert response.status_code == status.HTTP_200_OK

    # assert user can login after registration
    response = client.post(
        "/api/auth/login",
        json={"email": sample_user_data.email, "password": sample_user_data.password},
    )
    assert response.status_code == status.HTTP_200_OK
