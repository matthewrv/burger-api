from collections import OrderedDict
from typing import Any, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class Snapshot(OrderedDict[str, Any]):
    pass
