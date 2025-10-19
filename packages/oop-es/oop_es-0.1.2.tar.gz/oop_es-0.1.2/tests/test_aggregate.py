from oop_es import AggregateRoot, Event


class DummyEvent(Event):
    ...


class DummyAR(AggregateRoot):
    def __init__(self):
        super().__init__()
        self.test_events = []
        self.dummy_events = []

    def apply_event(self, event: Event):
        self.test_events.append(event)

    def apply_dummy_event(self, event: DummyEvent):
        self.dummy_events.append(event)


class TestAggregateRoot:
    def test_pop_events_returns_empty_list_when_no_events_present(self):
        aggregate = AggregateRoot()
        assert aggregate.pop_new_messages() == []

    def test_pop_applied_events(self):
        aggregate = DummyAR()
        event1 = Event()
        event2 = Event()
        aggregate.apply(event1)
        aggregate.apply(event2)
        message1, message2 = aggregate.pop_new_messages()
        assert message1.event == event1
        assert message2.event == event2
        assert message1.version == 0
        assert message2.version == 1
        assert aggregate.pop_new_messages() == []
        assert aggregate.test_events == [event1, event2]

    def test_handle_should_not_push_events(self):
        aggregate = DummyAR()
        event = DummyEvent()
        aggregate.handle(event)
        assert aggregate.test_events == []
        assert aggregate.dummy_events == [event]
        assert aggregate.pop_new_messages() == []

    def test_handle_all(self):
        aggregate = DummyAR()
        events = [Event(), Event(), Event()]

        aggregate.handle_all(events)

        assert aggregate.pop_new_messages() == []
        assert aggregate.test_events == events
