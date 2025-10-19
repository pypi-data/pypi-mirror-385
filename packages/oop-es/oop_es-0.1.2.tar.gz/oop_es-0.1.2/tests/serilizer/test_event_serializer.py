from dataclasses import dataclass

import pytest

from oop_es import Event
from oop_es.serializer.event_serializer import EventSerializer


@dataclass
class DummyEvent(Event):
    x: int
    y: str


class TestEventSerializer:
    def setup_method(self):
        self.sut = EventSerializer()

    def test_it_should_deserealize_serialized_event(self):
        event = DummyEvent(x=1, y="abc")
        deserialized = self.sut.deserialize(self.sut.serialize(event))
        assert isinstance(deserialized, DummyEvent)
        assert deserialized.x == 1
        assert deserialized.y == "abc"

    @pytest.mark.parametrize(
        "data",
        [
            {"class": "x.y"},
            {"data": {"x"}},
            {"data": {"y": "abc", "x": 1}, "class": "DummyEvent"},
            {"data": {"y": "abc", "x": 1}, "class": "module.DummyEvent"},
        ],
    )
    def test_it_should_fail_on_invalid_data(self, data):
        with pytest.raises(ValueError):
            self.sut.deserialize({"x": "y"})
