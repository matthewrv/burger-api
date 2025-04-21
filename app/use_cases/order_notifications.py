import abc
import collections
import datetime
import logging
from contextlib import contextmanager
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from pydantic import UUID4, BaseModel, Field
from sqlalchemy import Engine

from app.db import EngineDep, get_session
from app.repo.ingredients import IngredientsRepo
from app.repo.orders import OrderFull, OrdersRepo

__all__ = (
    "OrderListItem",
    "OrderSubscriber",
    "OrderNotificationManager",
    "NotificationDep",
)


class OrderListItem(BaseModel):
    id: UUID4
    number: int
    created_at: datetime.datetime = Field(alias="createdAt")
    name: str
    ingredients: list[UUID4] = Field(default_factory=list)
    status: str

    @classmethod
    def from_order_full(cls, order: OrderFull):
        return cls.model_validate(order, from_attributes=True, by_name=True)


class OrderSubscriber(abc.ABC):
    @abc.abstractmethod
    async def notify(self, recent_orders: dict[str, Any]) -> None:
        pass


class OrderNotificationManager:
    def __init__(self, engine: Engine):
        session_context = contextmanager(get_session)
        with session_context(engine) as session:
            ingredients_repo = IngredientsRepo(session)
            orders_repo = OrdersRepo(session, ingredients_repo)
            orders = orders_repo.get_recent_orders_full(limit=50)

        self.__orders = collections.deque(
            [OrderListItem.from_order_full(order) for order in orders]
        )
        self._subscribers: list[OrderSubscriber] = []

    async def sub(self, subscriber: OrderSubscriber):
        self._subscribers.append(subscriber)
        await subscriber.notify(self.get_message())

    def unsub(self, subscriber: OrderSubscriber):
        self._subscribers.remove(subscriber)

    async def pub(self, new_order: OrderFull):
        self.__orders.appendleft(OrderListItem.from_order_full(new_order))
        if len(self.__orders) > 50:
            self.__orders.pop()

        message = self.get_message()

        for sub in self._subscribers:
            try:
                await sub.notify(message)
            except Exception:
                logging.exception("Failed to notify about updated order")

    def get_message(self) -> dict[str, Any]:
        return {
            "orders": [
                order.model_dump(mode="json", by_alias=True) for order in self.__orders
            ],
            "total": 0,
            "totalToday": 0,
        }


@lru_cache
def get_order_notifications(engine: EngineDep):
    return OrderNotificationManager(engine)


NotificationDep = Annotated[OrderNotificationManager, Depends(get_order_notifications)]
