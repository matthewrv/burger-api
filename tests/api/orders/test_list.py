import asyncio

import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, aconnect_ws  # noqa: F401
from snapshottest.pytest import PyTestSnapshotTest

from app.db.tables.order import Order


@pytest.mark.anyio
@pytest.mark.now("2025-04-21T23:59:59.505731Z")
async def test_list_order_reset_today_count(
    client: AsyncClient,
    order: Order,
    snapshot: PyTestSnapshotTest,
) -> None:
    async with aconnect_ws("/api/orders/all", client) as websocket:  # type: AsyncWebSocketSession
        data = await websocket.receive_json()
        snapshot.assert_match(data)

        await asyncio.sleep(1)

        data = await websocket.receive_json()
        snapshot.assert_match(data)
