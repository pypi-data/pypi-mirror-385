from abc import ABC, abstractmethod
from typing import Generic, Type
from uuid import UUID

from oop_bus import EventBus

from oop_es.aggregate import Aggregate
from oop_es.store.event_store import EventStore


class AggregateRepository(ABC, Generic[Aggregate]):
    @abstractmethod
    async def load(self, uuid: UUID) -> Aggregate:
        ...

    @abstractmethod
    async def save(self, aggregate: Aggregate):
        ...


class SimpleAggregateRepository(AggregateRepository[Aggregate]):
    def __init__(self, store: EventStore, event_bus: EventBus, aggregate_class: Type[Aggregate]):
        self.store = store
        self.event_bus = event_bus
        self.aggregate_class = aggregate_class

    async def load(self, uuid: UUID) -> Aggregate:
        events = await self.store.load_events(uuid)
        aggregate_class = self.aggregate_class
        aggregate: Aggregate = aggregate_class(uuid)
        aggregate.handle_all(list(events.values()))

        return aggregate

    async def save(self, aggregate: Aggregate):
        uuid = aggregate.uuid
        messages = aggregate.pop_new_messages()

        if not messages:
            return

        await self.store.add(uuid, messages)
        for message in messages:
            await self.event_bus.dispatch(message.event)
