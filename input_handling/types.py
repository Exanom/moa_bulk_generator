from typing import TypedDict
from collections.abc import Callable

class CommandDict(TypedDict):
    name: str
    action: Callable