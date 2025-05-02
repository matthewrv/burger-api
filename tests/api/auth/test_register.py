import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import User
from tests.conftest import SampleUser


@pytest.mark.anyio
async def test_register(
    client: AsyncClient, session: AsyncSession, sample_user_data: SampleUser
) -> None:
    async with session.begin():
        result = await session.exec(select(User))
        users = result.all()
        assert len(users) == 0, f"Expected no users in db, but got {len(users)}"

    response = await client.post(
        "/api/auth/register",
        json={
            "name": sample_user_data.name,
            "email": sample_user_data.email,
            "password": sample_user_data.password,
        },
    )
    assert response.status_code == 200
    response_body = response.json()
    assert "accessToken" in response_body
    register_access_token = response_body["accessToken"]
    assert "refreshToken" in response_body

    async with session.begin():
        result = await session.exec(select(User))
        users = result.all()

        assert len(users) == 1

        user = users[0]
        assert user.email == sample_user_data.email
        assert user.name == sample_user_data.name

    # assert register access token is valid
    response = await client.get(
        "/api/auth/user", headers={"Authorization": register_access_token}
    )
    assert response.status_code == status.HTTP_200_OK

    # assert user can login after registration
    response = await client.post(
        "/api/auth/login",
        json={"email": sample_user_data.email, "password": sample_user_data.password},
    )
    assert response.status_code == status.HTTP_200_OK
