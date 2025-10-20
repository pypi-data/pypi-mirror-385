from typing import TypeVar


class Command:
    ...


CommandType = TypeVar("CommandType", bound=Command)
