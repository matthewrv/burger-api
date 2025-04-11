from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)


def test_get_user():
    response = client.get("/api/auth/user")
    assert response.status_code == 200
    assert response.json() == {"name": "test_user", "email": "test@example.com"}
