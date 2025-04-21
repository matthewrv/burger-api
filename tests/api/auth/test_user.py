from fastapi.testclient import TestClient
from snapshottest.pytest import PyTestSnapshotTest

from app import security
from tests.conftest import SampleUser


def test_get_user(
    client: TestClient, test_user: SampleUser, snapshot: PyTestSnapshotTest
) -> None:
    token = security.create_access_token(test_user)
    response = client.get(
        "/api/auth/user", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    snapshot.assert_match(response.json())
