import typing

import pytest
from fastapi.testclient import TestClient
from snapshottest.pytest import PyTestSnapshotTest

from tests.conftest import SampleUser


def test_get_user(
    client: TestClient, test_user: SampleUser, snapshot: PyTestSnapshotTest
) -> None:
    response = client.get(
        "/api/auth/user", headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    snapshot.assert_match(response.json())


@pytest.mark.parametrize(
    ["body", "remain_authenticated"],
    [
        pytest.param({"name": "new_name"}, True, id="name_only"),
        pytest.param({"email": "test2@example.com"}, False, id="email_only"),
        pytest.param({"password": "new_password"}, False, id="password_only"),
    ],
)
def test_update_user_happy_path(
    client: TestClient,
    test_user: SampleUser,
    snapshot: PyTestSnapshotTest,
    body: dict[str, typing.Any],
    remain_authenticated: bool,
) -> None:
    response = client.patch(
        "/api/auth/user",
        headers={"Authorization": f"Bearer {test_user.access_token}"},
        json=body,
    )

    assert response.status_code == 200
    snapshot.assert_match(response.json())

    response = client.get(
        "/api/auth/user",
        headers={"Authorization": f"Bearer {test_user.access_token}"},
    )
    if remain_authenticated:
        assert response.status_code == 200
    else:
        assert response.status_code == 403


def test_update_user_email_registered(
    client: TestClient,
    test_user: SampleUser,
    test_user_2: SampleUser,
    snapshot: PyTestSnapshotTest,
) -> None:
    body = {"email": test_user_2.email}

    response = client.patch(
        "/api/auth/user",
        headers={"Authorization": f"Bearer {test_user.access_token}"},
        json=body,
    )

    assert response.status_code == 400
    snapshot.assert_match(response.json())
