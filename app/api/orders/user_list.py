from typing import Annotated

from fastapi import Depends, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.db import User
from app.repo.orders import OrdersRepoDep
from app.repo.user import UserRepoDep
from app.security import get_current_user
from app.use_cases.order_notifications import (
    NotificationDep,
)

from ..router import api_router
from .common import WebSocketOrderNotifier

__all__ = ("get_profile_orders",)


async def _authenticate(
    user_repo: UserRepoDep, token: Annotated[str | None, Query()] = None
) -> User | None:
    if token is None:
        return None

    try:
        user = await get_current_user(user_repo, token)
    except HTTPException:  # catch 403
        return None

    return user


@api_router.websocket("/orders")
async def get_profile_orders(
    websocket: WebSocket,
    orders_repo: OrdersRepoDep,
    notifications: NotificationDep,
    user: Annotated[User | None, Depends(_authenticate)],
) -> None:
    await websocket.accept()

    if not user:
        try:
            await websocket.send_json(
                {"success": False, "message": "Invalid or missing token"}
            )
            await websocket.close()
        except WebSocketDisconnect:
            pass
        return

    async with WebSocketOrderNotifier(websocket, orders_repo, user) as notifier:
        await notifier.send_current_state()
        try:
            notifications.sub(notifier)
            while True:
                await websocket.receive_text()
        finally:
            notifications.unsub(notifier)
