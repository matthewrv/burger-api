import abc
import datetime
import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4, BaseModel, Field

from app.repo.orders import OrderFull

__all__ = (
    "OrderListItem",
    "OrderSubscriber",
    "OrderNotificationManager",
    "NotificationDep",
)


class OrderListItem(BaseModel):
    id: UUID4 = Field(alias="_id")
    number: int
    created_at: datetime.datetime = Field(alias="createdAt")
    name: str
    ingredients: list[UUID4] = Field(default_factory=list)
    status: str

    @classmethod
    def from_order_full(
        cls: type["OrderListItem"], order: OrderFull
    ) -> "OrderListItem":
        return cls.model_validate(order, from_attributes=True, by_name=True)


class OrderSubscriber(abc.ABC):
    @abc.abstractmethod
    async def notify(self, recent_orders: OrderFull) -> None:
        pass


class OrderNotificationManager:
    def __init__(self) -> None:
        self._subscribers: list[OrderSubscriber] = []

    def sub(self, subscriber: OrderSubscriber) -> None:
        self._subscribers.append(subscriber)

    def unsub(self, subscriber: OrderSubscriber) -> None:
        self._subscribers.remove(subscriber)

    async def pub(self, new_order: OrderFull) -> None:
        for sub in self._subscribers:
            try:
                await sub.notify(new_order)
            except Exception:
                logging.exception("Failed to notify about updated order")


@lru_cache
def get_order_notifications() -> OrderNotificationManager:
    return OrderNotificationManager()


async def _get_order_notifications_dep() -> OrderNotificationManager:
    return get_order_notifications()


NotificationDep = Annotated[
    OrderNotificationManager, Depends(_get_order_notifications_dep)
]
