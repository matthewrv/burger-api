from fastapi.testclient import TestClient

from app import security
from db.user import User


def test_get_user(client: TestClient, test_user: User):
    token = security.create_access_token(test_user)
    response = client.get(
        "/api/auth/user", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "user": {"name": test_user.name, "email": test_user.email}
    }
