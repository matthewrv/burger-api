import logging

import aio_pika

from app.repo.orders import OrderFull

from .inmemory import InMemoryOrderNotificationManager

ORDER_NOTIFICATIONS_EXCHANGE = "orders"


class _OrderNotificationBase:
    def __init__(self, connection: aio_pika.Connection):
        self._connection = connection
        self._channel: aio_pika.Channel = None
        self._exchange: aio_pika.Exchange = None

    async def __aenter__(self):
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            ORDER_NOTIFICATIONS_EXCHANGE, aio_pika.ExchangeType.FANOUT
        )

        return self

    async def __aexit__(self, *args):
        await self._channel.close()

    @staticmethod
    def _prepare_message(order: OrderFull) -> aio_pika.Message:
        body = order.model_dump_json().encode("utf8")
        return aio_pika.Message(body)

    @staticmethod
    def _decode_message(msg: aio_pika.Message) -> OrderFull:
        return OrderFull.model_validate_json(msg.body)


class OrderPublisher(_OrderNotificationBase):
    async def publish_order(self, order: OrderFull):
        try:
            msg = self._prepare_message(order)
            await self._exchange.publish(msg, routing_key="info")
        except Exception:
            logging.exception(f"Failed to publish info about order {order.id}")


class OrderConsumer(_OrderNotificationBase):
    def __init__(
        self,
        connection: aio_pika.Connection,
        notifications_manager: InMemoryOrderNotificationManager,
    ):
        super().__init__(connection)
        self._notifications_manager = notifications_manager

    async def __aenter__(self):
        await super().__aenter__()

        # start consuming on aenter
        queue = await self._channel.declare_queue(exclusive=True)
        await queue.bind(self._exchange)
        await queue.consume(self._consume)

        return self

    async def _consume(self, msg: aio_pika.Message):
        order = self._decode_message(msg)
        await self._notifications_manager.pub(order)
