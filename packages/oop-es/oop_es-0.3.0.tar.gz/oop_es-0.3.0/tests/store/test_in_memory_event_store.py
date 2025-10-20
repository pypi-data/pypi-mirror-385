from uuid import uuid4

import pytest

from oop_es.event import Event, Message
from oop_es.store.exception import WrongEventVersionException
from oop_es.store.in_memory_event_store import InMemoryEventStore


class TestInMemoryEventStore:
    @pytest.mark.asyncio
    async def test_load_events_empty(self):
        store = InMemoryEventStore()
        aggregate_id = uuid4()

        result = await store.load_events(aggregate_id)

        assert result == {}

    @pytest.mark.asyncio
    async def test_load_events(self):
        store = InMemoryEventStore()
        aggregate_id = uuid4()
        event1 = Event()
        event2 = Event()
        await store.add([Message(aggregate_id, event1, 0), Message(aggregate_id, event2, 1)])

        result = await store.load_events(aggregate_id)

        assert result == {0: event1, 1: event2}

    @pytest.mark.asyncio
    async def test_load_events_from(self):
        store = InMemoryEventStore()
        aggregate_id = uuid4()
        event1 = Event()
        event2 = Event()
        event3 = Event()
        await store.add([Message(aggregate_id, event1, 0), Message(aggregate_id, event2, 1), Message(aggregate_id, event3, 2)])

        result = await store.load_events_from(aggregate_id, 1)

        assert result == {1: event2, 2: event3}

    @pytest.mark.asyncio
    async def test_add_events_with_wrong_version(self):
        store = InMemoryEventStore()
        aggregate_id = uuid4()
        event1 = Event()
        event2 = Event()

        await store.add([Message(aggregate_id, event1, 0)])

        with pytest.raises(WrongEventVersionException):
            await store.add([Message(aggregate_id, event1, 0)])

        with pytest.raises(WrongEventVersionException):
            await store.add([Message(aggregate_id, event2, 2)])
