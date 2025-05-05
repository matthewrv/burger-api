import asyncio
import collections
from datetime import datetime, timedelta
from typing import Coroutine, Self

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from pydantic import UUID4, BaseModel, Field

from app.db import User
from app.db.utils import utc_now
from app.repo.orders import OrderFull, OrdersRepo
from app.use_cases.order_notifications import OrderListItem, OrderSubscriber


class OrderListItemResponse(BaseModel):
    id: UUID4
    number: int
    created_at: datetime = Field(alias="createdAt")
    name: str
    ingredients: list[UUID4] = Field(default_factory=list)
    status: str


class FeedState(BaseModel):
    orders: collections.deque[OrderListItem]
    total: int
    total_today: int = Field(alias="totalToday")


async def wait_until(dt: datetime) -> None:
    # sleep until the specified datetime
    now = utc_now()
    await asyncio.sleep((dt - now).total_seconds())


async def run_at(dt: datetime, coro: Coroutine[None, None, None]) -> None:
    try:
        await wait_until(dt)
        await coro
    except asyncio.CancelledError:
        coro.close()
        raise


class WebSocketOrderNotifier(OrderSubscriber):
    def __init__(
        self,
        websocket: WebSocket,
        orders_repo: OrdersRepo,
        user: User | None = None,
    ) -> None:
        if websocket.state == WebSocketState.DISCONNECTED:
            raise RuntimeError("WebSocket should be already connected")

        self._websocket = websocket
        self._user = user
        self._orders_repo = orders_repo

        self._state = FeedState(
            orders=collections.deque([]),
            total=0,
            totalToday=0,
        )
        self._reset_task: asyncio.Task[None] | None = None

    async def __aenter__(self) -> Self:
        await self._init_state()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # type: ignore[no-untyped-def]
        if self._reset_task:
            self._reset_task.cancel()
        return exc_type is WebSocketDisconnect

    async def _init_state(self) -> None:
        initial_orders = await self._orders_repo.get_recent_orders_full(user=self._user)
        total_orders, today_orders = await self._orders_repo.get_orders_count()

        now = utc_now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
            days=1
        )
        self._reset_task = asyncio.create_task(
            run_at(midnight, self._reset_today_orders())
        )

        self._state = FeedState(
            orders=collections.deque(
                [OrderListItem.from_order_full(order) for order in initial_orders]
            ),
            total=total_orders,
            totalToday=today_orders,
        )

        await self._send_current_state()

    async def _reset_today_orders(self) -> None:
        self._state.total_today = 0
        await self._send_current_state()

    async def notify(self, new_order: OrderFull) -> None:
        if self._user and self._user.id != new_order.owner_id:
            return

        self._state.orders.appendleft(OrderListItem.from_order_full(new_order))
        if len(self._state.orders) > 50:
            self._state.orders.pop()

        self._state.total += 1
        self._state.total_today += 1

        await self._send_current_state()

    async def _send_current_state(self) -> None:
        if self._websocket.state != WebSocketState.DISCONNECTED:
            message = self._state.model_dump(mode="json", by_alias=True)
            await self._websocket.send_json(message)
