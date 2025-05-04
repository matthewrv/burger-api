import functools
import inspect
from typing import Awaitable, Callable, Concatenate, ParamSpec, TypeVar

from app.db import SessionDep

__all__ = ("BaseRepo", "as_transaction")


class BaseRepo:
    def __init__(self, session: SessionDep) -> None:
        self._session = session


R = TypeVar("R", bound=BaseRepo)
P = ParamSpec("P")
T = TypeVar("T")


def as_transaction(
    method: Callable[Concatenate[R, P], Awaitable[T]],
) -> Callable[Concatenate[R, P], Awaitable[T]]:
    """
    Wraps method in transaction.

    Helps repos with shared session to execute several SQL queries
    in one transaction.
    """
    assert inspect.iscoroutinefunction(method), "Can only wrap async methods"

    @functools.wraps(method)
    async def wrapper(self: R, *args: P.args, **kwargs: P.kwargs) -> T:
        if self._session.in_transaction():
            return await method(self, *args, **kwargs)

        async with self._session.begin():
            return await method(self, *args, **kwargs)

    return wrapper
