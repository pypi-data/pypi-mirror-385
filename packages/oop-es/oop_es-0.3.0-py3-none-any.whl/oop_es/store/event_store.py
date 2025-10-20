from abc import ABC, abstractmethod
from typing import Dict
from uuid import UUID

from oop_es.event import Event, Message


class EventStore(ABC):
    @abstractmethod
    async def load_events(self, aggregate_id: UUID) -> Dict[int, Event]:
        ...

    @abstractmethod
    async def load_events_from(self, aggregate_id: UUID, version: int) -> Dict[int, Event]:
        ...

    @abstractmethod
    async def add(self, messages: list[Message]):
        ...
