import collections
import datetime

from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from pydantic import UUID4, BaseModel, Field

from app.repo.orders import OrderFull
from app.use_cases.order_notifications import OrderListItem, OrderSubscriber
from db.tables.user import User


class OrderListItemResponse(BaseModel):
    id: UUID4
    number: int
    created_at: datetime.datetime = Field(alias="createdAt")
    name: str
    ingredients: list[UUID4] = Field(default_factory=list)
    status: str


class FeedState(BaseModel):
    orders: collections.deque[OrderListItem]
    total: int
    total_today: int = Field(alias="totalToday")


class WebSocketOrderNotifier(OrderSubscriber):
    def __init__(
        self,
        websocket: WebSocket,
        initial_orders: list[OrderFull],
        user: User | None = None,
    ) -> None:
        if websocket.state == WebSocketState.DISCONNECTED:
            raise RuntimeError("WebSocket should be already connected")

        self._websocket = websocket
        self._user = user

        self._state = FeedState(
            orders=collections.deque(
                [OrderListItem.from_order_full(order) for order in initial_orders]
            ),
            total=0,
            totalToday=0,
        )

    async def notify(self, new_order: OrderFull) -> None:
        if self._user and self._user.id != new_order.owner_id:
            return

        self._state.orders.appendleft(OrderListItem.from_order_full(new_order))
        if len(self._state.orders) > 50:
            self._state.orders.pop()

        await self.send_current_state()

    async def send_current_state(self) -> None:
        if self._websocket.state != WebSocketState.DISCONNECTED:
            message = self._state.model_dump(mode="json", by_alias=True)
            await self._websocket.send_json(message)
