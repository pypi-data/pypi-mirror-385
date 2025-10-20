from typing import Type

import pytest

from oop_es.command.command import Command
from oop_es.command.command_bus import CommandBus, StandardCommandBus
from oop_es.command.command_handler import CommandHandler


class FakeCommand(Command):
    ...


class MockHandler(CommandHandler[Command]):
    def __init__(self, bus: CommandBus):
        self.bus = bus
        self.commands = []
        self.handling = True

    def command_type(self):
        return Command

    async def handle(self, command: Command) -> None:
        self.handling = True
        self.commands.append(command)
        await self.bus.handle(FakeCommand())
        self.handling = False


class FakeHandler(CommandHandler[FakeCommand]):
    def __init__(self, mock_handler: MockHandler):
        self.commands = []
        self.mock_handler = mock_handler

    def command_type(self) -> Type[FakeCommand]:
        return FakeCommand

    async def handle(self, command: FakeCommand) -> None:
        self.commands.append(command)
        assert not self.mock_handler.handling


class TestStandardCommandBus:
    def setup_method(self):
        self.command_bus = StandardCommandBus()
        self.mock_handler = MockHandler(self.command_bus)
        self.fake_handler = FakeHandler(self.mock_handler)

    @pytest.mark.asyncio
    async def test_handles_command_with_no_handler(self):
        await self.command_bus.handle(Command())

    @pytest.mark.asyncio
    async def test_handle_the_command_using_handler(self):
        command = Command()
        self.command_bus.subscribe(self.mock_handler)
        await self.command_bus.handle(command)
        assert self.mock_handler.commands == [command]

    @pytest.mark.asyncio
    async def test_auto_subscribe(self):
        command = Command()
        self.command_bus = StandardCommandBus([self.mock_handler])
        await self.command_bus.handle(command)
        assert self.mock_handler.commands == [command]

    @pytest.mark.asyncio
    async def test_handle_subcommand_after_processing_initiating_command_only(self):
        command = Command()
        self.command_bus.subscribe(self.mock_handler)
        self.command_bus.subscribe(self.fake_handler)
        await self.command_bus.handle(command)
        assert self.mock_handler.commands == [command]
        assert self.fake_handler.commands[0].__class__ == FakeCommand
