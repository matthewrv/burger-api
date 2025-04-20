import collections
import datetime
from threading import Lock
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import UUID4, BaseModel, Field
from sqlmodel import Session

from app.db import connect_to_db
from app.repo.ingredients import IngredientsRepo
from app.repo.orders import OrderFull, OrdersRepo

from ..router import api_router

__all__ = ("OrderListItemResponse", "get_orders")


class OrderListItemResponse(BaseModel):
    id: UUID4
    number: int
    created_at: datetime.datetime = Field(alias="createdAt")
    name: str
    ingredients: list[UUID4] = Field(default_factory=list)
    status: str


class OrdersConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []
        self._lock = Lock()

        engine = connect_to_db()
        with Session(engine) as session:
            ingredients_repo = IngredientsRepo(session)
            orders_repo = OrdersRepo(session, ingredients_repo)
            orders = orders_repo.get_recent_orders_full(limit=50)

        self.__orders = collections.deque(
            [
                OrderListItemResponse.model_validate(
                    order, from_attributes=True, by_name=True
                )
                for order in orders
            ]
        )

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        await websocket.send_json(self.get_message())

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.remove(websocket)

    def get_message(self) -> dict[str, Any]:
        return {
            "orders": [
                order.model_dump(mode="json", by_alias=True) for order in self.__orders
            ],
            "total": 0,
            "totalToday": 0,
        }

    async def broadcast_order(self, order: OrderFull) -> None:
        self.__orders.appendleft(
            OrderListItemResponse.model_validate(
                order, from_attributes=True, by_name=True
            )
        )
        if len(self.__orders) > 50:
            self.__orders.pop()

        message = self.get_message()

        for connection in self._connections:
            await connection.send_json(message)


manager = OrdersConnectionManager()


@api_router.websocket("/orders/all")
async def get_orders(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
