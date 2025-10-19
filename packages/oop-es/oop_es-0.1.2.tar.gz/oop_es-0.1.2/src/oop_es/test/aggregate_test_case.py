from typing import Callable, Generic, List

from oop_es.aggregate import Aggregate, Event


class AggregateTestCase(Generic[Aggregate]):
    def take(self, aggregate: Aggregate):
        self.aggregate = aggregate

    def having(self, events: List[Event]):
        for event in events:
            self.aggregate.handle(event)

    def when(self, function: Callable[[Aggregate], None]):
        function(self.aggregate)

    def then(self, events: List[Event]):
        assert events == [message.event for message in self.aggregate.pop_new_messages()]
