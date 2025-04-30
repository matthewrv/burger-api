import pytest
from fastapi import status
from httpx import AsyncClient

from tests.conftest import SampleUser


@pytest.mark.anyio
async def test_logout_happy_path(client: AsyncClient, test_user: SampleUser) -> None:
    response = await client.post(
        "/api/auth/logout", json={"token": test_user.refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK

    # assert all tokens are invalid after logout
    response = await client.get(
        "/api/auth/user", headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await client.post(
        "/api/auth/token", json={"token": test_user.refresh_token}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
