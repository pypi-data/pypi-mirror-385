"""Message structure for LLM conversations.

This module defines the Message TypedDict, which represents individual messages
in conversations with Large Language Models. Messages can represent user input,
assistant responses, system instructions, or tool call results.
"""

from typing import Any, NotRequired, TypedDict


class Message(TypedDict):
    """TypedDict representing a message in an LLM conversation.

    Message defines the structure for all messages exchanged in conversations with
    language models. It supports different message roles (user, assistant, system, tool)
    and includes optional fields for tool calling functionality. This structure is
    compatible with the OpenAI chat completions API format.

    Attributes:
        role (str): The role of the message sender. Valid values are:
            - "user": Messages from the user/human
            - "assistant": Responses from the LLM
            - "system": System instructions that guide the LLM's behavior
            - "tool": Results returned from tool function calls
        content (str): The text content of the message. For tool messages, this contains
            the stringified result of the tool execution.
        tool_call_id (NotRequired[str]): The ID of the tool call this message is responding to.
            Required for role="tool" messages, links the tool result back to the original
            tool call request.
        name (NotRequired[str]): The name of the tool that was called. Used with role="tool"
            to identify which tool produced this result.
        tool_calls (NotRequired[list[Any]]): List of tool calls requested by the assistant.
            Present when role="assistant" and the LLM wants to call one or more tools.
            Each tool call contains the function name, arguments, and a unique ID.

    Example:
        Creating different message types::

            # User message
            user_msg = Message(role="user", content="What is the weather in Paris?")

            # Assistant message without tools
            assistant_msg = Message(role="assistant", content="Let me check that for you.")

            # System message
            system_msg = Message(
                role="system",
                content="You are a helpful weather assistant."
            )

            # Tool result message
            tool_msg = Message(
                role="tool",
                content="Temperature: 18°C, Conditions: Partly cloudy",
                tool_call_id="call_abc123",
                name="get_weather"
            )

            # Assistant message with tool calls (typically created by LLM response)
            assistant_with_tools = Message(
                role="assistant",
                content="I'll check the weather for you.",
                tool_calls=[{
                    "id": "call_abc123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location": "Paris"}'
                    }
                }]
            )

    Note:
        - NotRequired fields are optional and may be omitted when not needed
        - Tool-related fields (tool_call_id, name, tool_calls) are only used in specific
          contexts: tool_call_id and name for tool messages, tool_calls for assistant messages
        - This structure is passed to and returned from LLMClient.invoke() and used throughout
          the conversation history in ReactAgent
    """

    role: str
    content: str
    tool_call_id: NotRequired[str]
    name: NotRequired[str]
    tool_calls: NotRequired[list[Any]]
