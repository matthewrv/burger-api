import time

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from db.user import User
from tests.conftest import SampleUser


def test_full_auth_flow(
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
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "accessToken" in response_body
    register_access_token = response_body["accessToken"]
    assert "refreshToken" in response_body
    register_refresh_token = response_body["refreshToken"]

    # assert register access token is valid
    response = client.get(
        "/api/auth/user", headers={"Authorization": register_access_token}
    )
    assert response.status_code == status.HTTP_200_OK

    # assert user can login after registration
    time.sleep(1)
    response = client.post(
        "/api/auth/login",
        json={"email": sample_user_data.email, "password": sample_user_data.password},
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "accessToken" in response_body
    initial_access_token = response_body["accessToken"]
    assert "refreshToken" in response_body
    initial_refresh_token = response_body["refreshToken"]

    # assert access token is valid
    response = client.get(
        "/api/auth/user", headers={"Authorization": initial_access_token}
    )
    assert response.status_code == status.HTTP_200_OK

    # refresh token
    time.sleep(1)
    response = client.post("/api/auth/token", json={"token": initial_refresh_token})
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "accessToken" in response_body
    refreshed_access_token = response_body["accessToken"]
    assert "refreshToken" in response_body
    refreshed_refresh_token = response_body["refreshToken"]

    # assert after refresh intial tokens are invalid
    response = client.get(
        "/api/auth/user", headers={"Authorization": initial_access_token}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = client.post("/api/auth/token", json={"token": initial_refresh_token})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # assert refreshed tokens are valid
    response = client.get(
        "/api/auth/user", headers={"Authorization": refreshed_access_token}
    )
    assert response.status_code == status.HTTP_200_OK

    time.sleep(1)
    response = client.post("/api/auth/logout", json={"token": refreshed_refresh_token})
    assert response.status_code == status.HTTP_200_OK

    # assert all tokens are invalid after logout
    response = client.get(
        "/api/auth/user", headers={"Authorization": refreshed_access_token}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post("/api/auth/token", json={"token": refreshed_refresh_token})
    assert response.status_code == status.HTTP_403_FORBIDDEN
