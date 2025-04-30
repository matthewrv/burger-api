from fastapi import status
from fastapi.testclient import TestClient
from snapshottest.pytest import PyTestSnapshotTest

from tests.conftest import SampleUser


def test_login_happy_path(
    client: TestClient, test_user: SampleUser, snapshot: PyTestSnapshotTest
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": test_user.password},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.keys() == {"refreshToken", "accessToken", "user", "success"}
    snapshot.assert_match(response_json["user"])

    assert "accessToken" in response_json
    access_token = response_json["accessToken"]
    assert "refreshToken" in response_json

    # assert access token is valid
    response = client.get("/api/auth/user", headers={"Authorization": access_token})
    assert response.status_code == status.HTTP_200_OK


def test_login_invalid_password(
    client: TestClient, test_user: SampleUser, snapshot: PyTestSnapshotTest
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "not_actual_password"},
    )
    assert response.status_code == 400
    snapshot.assert_match(response.json())


def test_login_invalid_email(
    client: TestClient, test_user: SampleUser, snapshot: PyTestSnapshotTest
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "not" + test_user.email, "password": test_user.password},
    )
    assert response.status_code == 400
    snapshot.assert_match(response.json())
