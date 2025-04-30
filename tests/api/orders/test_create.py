import uuid

import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, aconnect_ws  # noqa: F401
from snapshottest.pytest import PyTestSnapshotTest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.ingredient import Ingredient
from db.order import Order
from tests.conftest import SampleUser


@pytest.mark.anyio
@pytest.mark.now("2025-04-21T10:50:49.105731Z")
async def test_create_order_happy_path(
    session: AsyncSession,
    client: AsyncClient,
    test_user: SampleUser,
    ingredients: list[Ingredient],
    snapshot: PyTestSnapshotTest,
) -> None:
    bun = next(ingredient for ingredient in ingredients if ingredient.type == "bun")
    ingredients.remove(bun)

    burger_ingredients = [str(ingredient.id) for ingredient in ingredients]
    burger_ingredients = [str(bun.id), *burger_ingredients, str(bun.id)]

    async with aconnect_ws("/api/orders/all", client) as websocket:  # type: AsyncWebSocketSession
        data = await websocket.receive_json()
        snapshot.assert_match(data)

        response = await client.post(
            "/api/orders",
            json={"ingredients": burger_ingredients},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == 200
        snapshot.assert_match(response.json())

        data = await websocket.receive_json()
        snapshot.assert_match(data)

    async with session.begin():
        result = await session.exec(select(Order))
        db_orders = result.all()
        assert len(db_orders) == 1


@pytest.mark.anyio
async def test_create_order_fail(
    session: AsyncSession,
    client: AsyncClient,
    test_user: SampleUser,
) -> None:
    response = await client.post(
        "/api/orders",
        json={"ingredients": [str(uuid.uuid4())]},
        headers={"Authorization": f"Bearer {test_user.access_token}"},
    )
    assert response.status_code == 422

    async with session.begin():
        db_orders = await session.exec(select(Order))
        assert len(db_orders.all()) == 0

    response_body = response.json()
    assert response_body == {"error": "unknown ingredients", "success": False}
