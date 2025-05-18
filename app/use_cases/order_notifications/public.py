from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import aio_pika
from fastapi import Depends, FastAPI, Request, WebSocket

from app.repo.orders import OrderFull

from .inmemory import InMemoryOrderNotificationManager, OrderSubscriber
from .rabbitmq import OrderConsumer, OrderPublisher


@asynccontextmanager
async def lifespan(
    app: FastAPI, connection: aio_pika.abc.AbstractRobustConnection
) -> AsyncGenerator[None, None]:
    notifications_manager = InMemoryOrderNotificationManager()

    # start rabbitmq consumer and publisher
    async with (
        OrderConsumer(connection, notifications_manager),
        OrderPublisher(connection) as publisher,
    ):
        # enrich state - required for NotificationDep
        app.state.order_publisher = publisher
        app.state.notification_manager = notifications_manager

        yield


class NotificationsUseCase:
    def __init__(
        self,
        notifications_manager: InMemoryOrderNotificationManager,
        order_publisher: OrderPublisher,
    ):
        self._in_process_manager = notifications_manager
        self._inter_proccess_publisher = order_publisher

    async def pub(self, order: OrderFull) -> None:
        await self._inter_proccess_publisher.publish_order(order)

    def sub(self, subscriber: OrderSubscriber) -> None:
        self._in_process_manager.sub(subscriber)

    def unsub(self, subscriber: OrderSubscriber) -> None:
        self._in_process_manager.unsub(subscriber)


async def get_notifications_use_case(
    request: Request = None,  # type: ignore[assignment]
    ws: WebSocket = None,  # type: ignore[assignment]
) -> NotificationsUseCase:
    if request:
        return NotificationsUseCase(
            request.app.state.notification_manager,
            request.app.state.order_publisher,
        )

    if ws:
        return NotificationsUseCase(
            ws.app.state.notification_manager,
            ws.app.state.order_publisher,
        )

    raise RuntimeError("This should never have happened")


NotificationDep = Annotated[NotificationsUseCase, Depends(get_notifications_use_case)]


__all__ = ("lifespan", "OrderSubscriber", "NotificationDep")
