import logging

from app.repo.orders import OrderFull

from .abc import AbstractOrderPublisher, OrderSubscriber


class InMemoryOrderNotificationManager(AbstractOrderPublisher):
    """Broadcasts all created and updated orders to all subscribers within current process."""

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


__all__ = (
    "OrderSubscriber",
    "InMemoryOrderNotificationManager",
)
