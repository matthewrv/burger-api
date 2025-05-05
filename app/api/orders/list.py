from fastapi import WebSocket

from app.repo.orders import OrdersRepoDep
from app.use_cases.order_notifications import NotificationDep

from ..router import api_router
from .common import WebSocketOrderNotifier

__all__ = "get_orders"


@api_router.websocket("/orders/all")
async def get_orders(
    websocket: WebSocket,
    order_notifications: NotificationDep,
    orders_repo: OrdersRepoDep,
) -> None:
    await websocket.accept()
    async with WebSocketOrderNotifier(websocket, orders_repo) as notifier:
        try:
            order_notifications.sub(notifier)
            while True:
                await websocket.receive_text()
        finally:
            order_notifications.unsub(notifier)
