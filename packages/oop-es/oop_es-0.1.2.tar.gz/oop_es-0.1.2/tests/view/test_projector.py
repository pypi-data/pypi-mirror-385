from typing import List

import pytest
from oop_bus import EventBus

from oop_es import Event
from oop_es.view.projector import Projector


class MyTestEvent(Event): ...


class MyTestEvent2(Event): ...


class MyProjector(Projector):
    def __init__(self):
        self.test1_called = False
        self.test2_called = False

    def get_event_names(self) -> List[str]:
        return [MyTestEvent.__name__, MyTestEvent2.__name__]

    async def apply_my_test_event(self, event: MyTestEvent):
        if isinstance(event, MyTestEvent):
            self.test1_called = True

    async def apply_my_test_event2(self, event: MyTestEvent2):
        if isinstance(event, MyTestEvent2):
            self.test2_called = True


class TestMyProjector:
    @pytest.mark.asyncio
    async def test_it_should_call_different_methods(self):
        bus = EventBus()
        event = MyTestEvent()
        event2 = MyTestEvent2()
        projector = MyProjector()
        bus.listen(projector)

        await bus.dispatch(event)
        await bus.dispatch(event2)

        assert projector.test1_called
        assert projector.test2_called