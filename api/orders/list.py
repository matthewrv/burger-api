import datetime

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import UUID4, BaseModel, Field

from app.use_cases.order_notifications import NotificationDep, OrderSubscriber

from ..router import api_router

__all__ = ("OrderListItemResponse", "get_orders")


class OrderListItemResponse(BaseModel):
    id: UUID4
    number: int
    created_at: datetime.datetime = Field(alias="createdAt")
    name: str
    ingredients: list[UUID4] = Field(default_factory=list)
    status: str


class WebSocketOrderNotifier(OrderSubscriber):
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket
        self._connected = False

    async def connect(self):
        if not self._connected:
            await self._websocket.accept()
            self._connected = True

    async def notify(self, recent_orders: list[dict]) -> None:
        await self._websocket.send_json(recent_orders)


@api_router.websocket("/orders/all")
async def get_orders(
    websocket: WebSocket, order_notifications: NotificationDep
) -> None:
    notifier = WebSocketOrderNotifier(websocket)
    await notifier.connect()
    try:
        await order_notifications.sub(notifier)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        order_notifications.unsub(notifier)
