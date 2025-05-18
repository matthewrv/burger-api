import abc

from app.repo.orders import OrderFull


class OrderSubscriber(abc.ABC):
    @abc.abstractmethod
    async def notify(self, new_order: OrderFull) -> None:
        pass


class AbstractOrderPublisher(abc.ABC):
    @abc.abstractmethod
    async def pub(self, order: OrderFull) -> None:
        pass
