from collections import defaultdict
from typing import Dict
from uuid import UUID

from ..event import Event, Message
from .event_store import EventStore
from .exception import WrongEventVersionException


class InMemoryEventStore(EventStore):
    def __init__(self):
        self.events = defaultdict(list)

    async def load_events(self, aggregate_id: UUID) -> Dict[int, Event]:
        return {k: v for k, v in enumerate(self.events[str(aggregate_id)])}

    async def load_events_from(self, aggregate_id: UUID, version: int) -> Dict[int, Event]:
        events = self.events[str(aggregate_id)]
        if version >= len(events):
            return {}

        return {k: v for k, v in enumerate(events[version:], start=version)}

    async def add(self, messages: list[Message]):
        for message in messages:
            saved_events = self.events[str(message.uuid)]
            if message.version != len(saved_events):
                raise WrongEventVersionException(
                    f"Wrong event version {message.version}, should be {len(saved_events)}"
                )

            saved_events.append(message.event)
