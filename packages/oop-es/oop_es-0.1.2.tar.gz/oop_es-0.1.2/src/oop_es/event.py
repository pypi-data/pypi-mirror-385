from datetime import datetime
from typing import Any, Dict

from oop_bus import Event as OopEvent


class Event(OopEvent):
    def serialize(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

    @classmethod
    def deserialize(cls, data: Dict[str, Any]):
        instance = cls(**data)
        return instance

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


class Message:
    def __init__(
        self, event: Event, version: int, emitted_at: datetime | None = None, meta: dict[str, Any] | None = None
    ) -> None:
        self.event = event
        self.version = version
        self.emitted_at = emitted_at or datetime.now()
        self.meta = meta or {}
