import functools
from typing import Callable, Concatenate, ParamSpec, TypeVar

from app.db import SessionDep

__all__ = ("BaseRepo", "as_transaction")


class BaseRepo:
    def __init__(self, session: SessionDep) -> None:
        self._session = session


R = TypeVar("R", bound=BaseRepo)
P = ParamSpec("P")
T = TypeVar("T")


def as_transaction(
    method: Callable[Concatenate[R, P], T],
) -> Callable[Concatenate[R, P], T]:
    """
    Wraps method in transaction.

    Helps repos with shared session to execute several SQL queries
    in one transaction.
    """

    @functools.wraps(method)
    def wrapper(self: R, *args: P.args, **kwargs: P.kwargs) -> T:
        if self._session.in_transaction():
            return method(self, *args, **kwargs)

        with self._session.begin():
            return method(self, *args, **kwargs)

    return wrapper
