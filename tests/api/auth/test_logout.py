
from fastapi import status
from fastapi.testclient import TestClient

from tests.conftest import SampleUser


def test_logout_happy_path(client: TestClient, test_user: SampleUser) -> None:
    response = client.post("/api/auth/logout", json={"token": test_user.refresh_token})
    assert response.status_code == status.HTTP_200_OK

    # assert all tokens are invalid after logout
    response = client.get(
        "/api/auth/user", headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post("/api/auth/token", json={"token": test_user.refresh_token})
    assert response.status_code == status.HTTP_403_FORBIDDEN
