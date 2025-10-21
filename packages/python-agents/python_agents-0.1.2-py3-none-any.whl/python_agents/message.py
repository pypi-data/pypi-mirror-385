from typing import Any, TypedDict


class Message(TypedDict):
    role: str
    content: str
    tool_call_id: str = None
    name: str = None
    tool_calls: list[Any] = None
