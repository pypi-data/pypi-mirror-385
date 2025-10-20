from functools import reduce
from typing import Generic, TypeVar


from ..event import Message

View = TypeVar("View")

class Projector(Generic[View]):
    async def __call__(self, message: Message):
        event = message.event
        event_name_snake_case = reduce(
            lambda x, y: x + ("_" if y.isupper() else "") + y, event.get_name().split(".")[-1]
        ).lower()
        method_name = f"apply_{event_name_snake_case}"
        try:
            apply_method = getattr(self, method_name)
        except AttributeError:
            return
        await apply_method(message)
