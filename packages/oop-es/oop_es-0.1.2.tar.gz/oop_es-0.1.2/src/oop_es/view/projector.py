from functools import reduce
from typing import Generic, TypeVar

from oop_bus import EventListener

from .. import Event

View = TypeVar("View")

class Projector(EventListener, Generic[View]):
    async def __call__(self, event: Event):
        event_name_snake_case = reduce(
            lambda x, y: x + ("_" if y.isupper() else "") + y, event.get_name().split(".")[-1]
        ).lower()
        method_name = f"apply_{event_name_snake_case}"
        apply_method = getattr(self, method_name)
        await apply_method(event)
