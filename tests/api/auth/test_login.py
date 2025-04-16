from fastapi.testclient import TestClient

from db.user import User
from tests.conftest import TEST_USER_PASSWORD


def test_login(client: TestClient, test_user: User):
    response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.keys() == {"refreshToken", "accessToken", "user"}
    assert response_json["user"] == {"name": test_user.name, "email": test_user.email}
