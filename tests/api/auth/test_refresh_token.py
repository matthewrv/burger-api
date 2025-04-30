import pytest
from fastapi import status
from httpx import AsyncClient

from tests.conftest import SampleUser


@pytest.mark.anyio
async def test_refresh_token_happy_path(
    client: AsyncClient, test_user: SampleUser
) -> None:
    response = await client.post(
        "/api/auth/token", json={"token": test_user.refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "accessToken" in response_body
    refreshed_access_token = response_body["accessToken"]
    assert "refreshToken" in response_body
    refreshed_refresh_token = response_body["refreshToken"]

    # assert after refresh intial tokens are invalid
    response = await client.get(
        "/api/auth/user", headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = await client.post(
        "/api/auth/token", json={"token": test_user.refresh_token}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # assert refreshed access_token is valid
    response = await client.get(
        "/api/auth/user", headers={"Authorization": refreshed_access_token}
    )
    assert response.status_code == status.HTTP_200_OK

    # assert refreshed refresh_token is valid
    response = await client.post(
        "/api/auth/token", json={"token": refreshed_refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK
