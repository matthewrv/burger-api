from typing import Annotated

from fastapi import Depends, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.db import SessionDep
from app.repo.orders import OrdersRepoDep
from app.security import get_current_user
from app.use_cases.order_notifications import (
    NotificationDep,
)
from db.user import User

from ..router import api_router
from .common import WebSocketOrderNotifier

__all__ = "get_profile_orders"


async def _authenticate(
    session: SessionDep, token: Annotated[str, Query()] = None
) -> User | None:
    if token is None:
        return None

    try:
        user = await get_current_user(session, token)
    except HTTPException:  # catch 403
        return None

    return user


@api_router.websocket("/orders")
async def get_profile_orders(
    websocket: WebSocket,
    orders_repo: OrdersRepoDep,
    notifications: NotificationDep,
    user: Annotated[User | None, Depends(_authenticate)],
):
    await websocket.accept()

    if not user:
        await websocket.send_json(
            {"success": False, "message": "Invalid or missing token"}
        )
        await websocket.close()
        return

    initial_orders = orders_repo.get_recent_orders_full(limit=50, user=user)
    notifier = WebSocketOrderNotifier(websocket, initial_orders, user)
    await notifier.send_current_state()

    try:
        notifications.sub(notifier)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifications.unsub(notifier)
