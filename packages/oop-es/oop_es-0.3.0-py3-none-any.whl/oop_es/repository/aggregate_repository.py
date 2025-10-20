from abc import ABC, abstractmethod
from typing import Generic, List, Type
from uuid import UUID

from oop_es.aggregate import Aggregate
from oop_es.exception import EventStoreException
from oop_es.store.event_store import EventStore
from oop_es.view.projector import Projector


class NotFoundException(EventStoreException):
    ...

class AggregateRepository(ABC, Generic[Aggregate]):
    @abstractmethod
    async def load(self, uuid: UUID) -> Aggregate:
        ...

    @abstractmethod
    async def save(self, aggregate: Aggregate):
        ...


class SimpleAggregateRepository(AggregateRepository[Aggregate]):
    def __init__(self, store: EventStore, projectors: List[Projector], aggregate_class: Type[Aggregate]):
        self.store = store
        self.projectors = projectors
        self.aggregate_class = aggregate_class

    async def load(self, uuid: UUID) -> Aggregate:
        events = await self.store.load_events(uuid)
        if not events:
            raise NotFoundException("No aggregate found", {"uuid": str(uuid)})
        aggregate_class = self.aggregate_class
        aggregate: Aggregate = aggregate_class(uuid)
        aggregate.handle_all(list(events.values()))

        return aggregate

    async def save(self, aggregate: Aggregate):
        messages = aggregate.pop_new_messages()

        if not messages:
            return

        await self.store.add(messages)
        for message in messages:
            for projector in self.projectors:
                await projector(message)
