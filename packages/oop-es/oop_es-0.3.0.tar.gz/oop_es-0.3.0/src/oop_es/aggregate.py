from functools import reduce
from typing import TypeVar
from uuid import UUID, uuid4

from oop_es.event import Event, Message


class AggregateRoot:
    def __init__(self, uuid: UUID | None = None):
        self.__events: dict[int, Event] = {}
        self.__version: int = 0

        self.uuid = uuid or uuid4()

    def pop_new_messages(self) -> list[Message]:
        events = self.__events
        self.__events = {}
        return [Message(self.uuid, event, version) for version, event in events.items()]

    def apply(self, event: Event):
        self.__events[self.__version] = event
        self.handle(event)
        self.__version += 1

    def handle(self, event: Event):
        event_name_snake_case = reduce(
            lambda x, y: x + ("_" if y.isupper() else "") + y, event.get_name().split(".")[-1]
        ).lower()
        method_name = f"apply_{event_name_snake_case}"
        apply_method = getattr(self, method_name)
        apply_method(event)

    def handle_all(self, events: list[Event]):
        for event in events:
            self.handle(event)
            self.__version += 1


Aggregate = TypeVar("Aggregate", bound=AggregateRoot)
