from typing import Optional
from unittest.mock import AsyncMock, call
from uuid import UUID, uuid4

import pytest

from oop_es import Event
from oop_es.aggregate import AggregateRoot
from oop_es.repository.aggregate_repository import NotFoundException, SimpleAggregateRepository
from oop_es.store.event_store import EventStore
from oop_es.view import Projector


class DummyEvent(Event):
    ...


class DummyAR(AggregateRoot):
    def __init__(self, uuid: Optional[UUID] = None):
        super().__init__(uuid)
        self.dummy_events = []

    def apply_dummy_event(self, event: DummyEvent):
        self.dummy_events.append(event)


class TestSimpleAggregateRepository:
    def setup_method(self):
        self.store = AsyncMock(spec=EventStore)
        self.projectors = [AsyncMock(spec=Projector)]
        self.sut = SimpleAggregateRepository[DummyAR](self.store, self.projectors, DummyAR)

    @pytest.mark.asyncio
    async def test_it_should_load_aggregate_by_uuid(self):
        uuid = uuid4()
        self.store.load_events.return_value = {0: DummyEvent(), 1: DummyEvent()}

        aggregate = await self.sut.load(uuid)

        self.store.load_events.assert_awaited_once_with(uuid)
        assert isinstance(aggregate, DummyAR)
        assert aggregate.uuid == uuid
        assert len(aggregate.dummy_events) == 2
        assert len(aggregate.pop_new_messages()) == 0


    @pytest.mark.asyncio
    async def test_it_should_fail_if_no_events_loaded(self):
        uuid = uuid4()
        self.store.load_events.return_value = {}
        with pytest.raises(NotFoundException):
            await self.sut.load(uuid)


    @pytest.mark.asyncio
    async def test_it_should_return_early_if_nothing_to_save(self):
        aggregate = DummyAR()

        await self.sut.save(aggregate)

        self.store.add.assert_not_awaited()
        self.projectors[0].assert_not_awaited()

    @pytest.mark.asyncio
    async def test_it_should_save_and_dispatch_events(self):
        aggregate = DummyAR()
        event1 = DummyEvent()
        event2 = DummyEvent()
        aggregate.apply(event1)
        aggregate.apply(event2)

        await self.sut.save(aggregate)

        message1, message2 = self.store.add.call_args[0][0]
        assert event1 == message1.event
        assert event2 == message2.event
        assert 0 == message1.version
        assert 1 == message2.version
        self.projectors[0].assert_has_awaits([call(message1), call(message2)])
