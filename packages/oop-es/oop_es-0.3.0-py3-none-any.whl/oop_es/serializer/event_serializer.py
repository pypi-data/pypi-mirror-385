import importlib
from typing import Any, Dict

from .. import Event
from .serializer import Serializer


class EventSerializer(Serializer):
    def serialize(self, item: object) -> Dict[str, Any]:
        if not isinstance(item, Event):
            raise TypeError("item must be of type Event")

        return {"class": f"{item.__class__.__module__}.{item.__class__.__name__}", "data": item.serialize()}

    def deserialize(self, data: Dict[str, Any]) -> object:
        try:
            class_path = data["class"]
            event_data = data["data"]
            module_path, class_name = class_path.rsplit(".", 1)
        except (KeyError, ValueError) as exception:
            raise ValueError("Data is not a serialized Event") from exception

        module = importlib.import_module(module_path)
        event_cls = getattr(module, class_name, None)
        if not event_cls:
            raise ValueError(f"Unknown event class: {class_path}")
        return event_cls.deserialize(event_data)
