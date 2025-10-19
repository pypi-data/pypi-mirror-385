from abc import ABC, abstractmethod
from typing import Any, Dict


class Serializer(ABC):
    @abstractmethod
    def serialize(self, item: object) -> Dict[str, Any]:
        ...

    @abstractmethod
    def deserialize(self, data: Dict[str, Any]) -> object:
        ...
