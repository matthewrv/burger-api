from fastapi.testclient import TestClient

from tests.conftest import SampleUser


def test_login(client: TestClient, test_user: SampleUser) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": test_user.password},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.keys() == {"refreshToken", "accessToken", "user", "success"}
    assert response_json["user"] == {"name": test_user.name, "email": test_user.email}
