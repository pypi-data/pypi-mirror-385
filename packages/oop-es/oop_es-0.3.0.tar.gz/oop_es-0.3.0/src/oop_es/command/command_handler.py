from abc import ABC, abstractmethod
from typing import Generic, Type

from oop_es.command.command import CommandType


class CommandHandler(ABC, Generic[CommandType]):
    @abstractmethod
    def command_type(self) -> Type[CommandType]:
        ...

    @abstractmethod
    async def handle(self, command: CommandType) -> None:
        ...
