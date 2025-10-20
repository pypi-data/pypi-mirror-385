from uuid import uuid4

import pytest

from oop_es import Event
from oop_es.event import Message
from oop_es.view.projector import Projector


class MyTestEvent(Event): ...


class MyTestEvent2(Event): ...


class MyTestEvent3(Event): ...


class MyProjector(Projector):
    def __init__(self):
        self.test1_called = False
        self.test2_called = False

    async def apply_my_test_event(self, message: Message):
        if isinstance(message.event, MyTestEvent):
            self.test1_called = True

    async def apply_my_test_event2(self, message: Message):
        if isinstance(message.event, MyTestEvent2):
            self.test2_called = True


class TestMyProjector:
    @pytest.mark.asyncio
    async def test_it_should_call_different_methods(self):
        event = MyTestEvent()
        message = Message(uuid4(), event, 0)
        event2 = MyTestEvent2()
        message2 = Message(uuid4(), event2, 1)
        projector = MyProjector()

        assert not projector.test1_called
        assert not projector.test2_called

        await projector(message)

        assert projector.test1_called
        assert not projector.test2_called

        await projector(message2)

        assert projector.test1_called
        assert projector.test2_called

    @pytest.mark.asyncio
    async def test_it_should_not_fail_for_unsupported_event_types(self):
        event = MyTestEvent3()
        message = Message(uuid4(), event, 0)

        projector = MyProjector()

        await projector(message)
