"""LLM client with tool calling capabilities.

This module provides the LLMClient class, which wraps the OpenAI API to provide
a simple interface for interacting with Large Language Models. It supports automatic
tool calling, where Python functions are converted to tool schemas and executed
when the LLM requests them.
"""

import json

from openai import AsyncOpenAI

from python_agents import tools
from python_agents.message import Message


class LLMClient:
    """Client for interacting with Large Language Models with tool calling support.

    LLMClient provides a high-level interface for calling LLMs through the OpenAI API.
    It automatically handles tool registration, schema generation from Python functions,
    and tool execution when requested by the LLM. By default, it uses OpenRouter as the
    API endpoint, but can be configured for any OpenAI-compatible service.

    Attributes:
        model_name (str): Default model to use for LLM calls (e.g., "openai/gpt-4").
        client (AsyncOpenAI): Underlying async OpenAI client.
        tools (dict): Dictionary mapping tool names to their functions and schemas.

    Example:
        Basic usage without tools::

            client = LLMClient("openai/gpt-4.1-mini")
            response = await client.invoke("What is 2+2?")
            print(response.message.content)

        Using tools with automatic function calling::

            def calculator(operation: str, a: int, b: int) -> int:
                '''Perform arithmetic operations.

                Args:
                    operation: The operation ('+', '-', '*', '/')
                    a: First number
                    b: Second number

                Returns:
                    Result of the operation
                '''
                if operation == "+":
                    return a + b
                # ... more operations

            client = LLMClient("openai/gpt-4-turbo")
            client.add_tool(calculator)
            response = await client.invoke("What is 15 + 27?")
            # LLM will automatically call calculator tool
    """

    def __init__(
        self,
        model_name: str = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        """Initialize the LLM client.

        Args:
            model_name (str, optional): Default model name to use for requests.
                Can be overridden per request. Format depends on the API provider
                (e.g., "openai/gpt-4-turbo" for OpenRouter). Defaults to None.
            base_url (str, optional): Base URL for the OpenAI-compatible API.
                Defaults to "https://openrouter.ai/api/v1".

        Note:
            Requires OPENAI_API_KEY environment variable to be set for authentication.
            When using OpenRouter, this should be your OpenRouter API key.
        """
        self.model_name = model_name
        self.client = AsyncOpenAI(base_url=base_url)
        self.tools = {}

    def add_tool(self, func):
        """Register a Python function as a tool that the LLM can call.

        The function is automatically converted to an OpenAI function schema using
        introspection of the function signature, type hints, and docstring. The LLM
        can then request to call this tool during conversation.

        Args:
            func (callable): A Python function to register as a tool. The function should have:
                - Type hints for all parameters
                - A clear docstring describing what it does
                - A descriptive name
                All parameters must be JSON-serializable types (str, int, float, bool).

        Example::

            def get_weather(location: str, units: str = "celsius") -> str:
                '''Get the weather for a location.

                Args:
                    location: City name
                    units: Temperature units (celsius or fahrenheit)
                '''
                # Implementation
                return f"Weather in {location}: 20°{units[0].upper()}"

            client.add_tool(get_weather)

        Note:
            The function will be called synchronously when the LLM requests it,
            and the result will be stringified before being returned to the LLM.
        """
        schema = tools.create_tool_schema(func)
        self.tools[func.__name__] = {"func": func, "schema": schema}

    async def _make_llm_call(self, messages: list[Message], model_name: str = None):
        """Make a low-level call to the LLM API.

        Internal method that handles the actual API request to the LLM, including
        passing available tools in the request.

        Args:
            messages (list[Message]): List of conversation messages to send.
            model_name (str, optional): Model to use. If None, uses self.model_name.

        Returns:
            ChatCompletionChoice: The first choice from the LLM response, containing
                the message and optionally tool calls.
        """
        available_tools = [tool["schema"] for tool in self.tools.values()]

        response = await self.client.chat.completions.create(
            model=model_name or self.model_name,
            messages=messages,
            tools=available_tools,
        )

        return response.choices[0]

    async def _make_tool_call(self, tc):
        """Execute a tool call requested by the LLM.

        Internal method that executes a registered tool function with the arguments
        provided by the LLM. The result is stringified for return to the LLM.

        Args:
            tc: Tool call object from OpenAI API containing function name and arguments.

        Returns:
            tuple: A 3-tuple of (tool_call_id, tool_name, tool_result_str).

        Raises:
            RuntimeError: If the LLM requests a tool that hasn't been registered.
        """
        tool_name = tc.function.name
        tool_args = tc.function.arguments
        tool_args = json.loads(tool_args) if tool_args else {}

        if tool_name in self.tools:
            func = self.tools[tool_name]["func"]
            tool_result = str(func(**tool_args))
        else:
            raise RuntimeError(f"LLM tried to call unknown tool '{tool_name}'")
        return tc.id, tool_name, tool_result

    async def invoke(self, query: list[Message] | Message | str, model_name=None, verbose: bool = False):
        """Send a query to the LLM and handle any tool calls.

        This is the main method for interacting with the LLM. It accepts various input
        formats, calls the LLM, automatically executes any requested tool calls, and
        returns the final response. The method handles one round of tool calling - if
        the LLM requests tools, they are all executed, and then a final LLM call is made
        with the tool results.

        Args:
            query (list[Message] | Message | str): The input to send to the LLM.
                Can be:
                - str: Converted to a single user message
                - Message: Single message to send
                - list[Message]: Full conversation history
            model_name (str, optional): Model to use for this request. Overrides
                the default model_name set during initialization. Defaults to None.
            verbose (bool, optional): If True, prints response content to stdout when
                no tools are called. Defaults to False.

        Returns:
            ChatCompletionChoice: The LLM's response containing the message content.
                Access the text response via `response.message.content`.

        Raises:
            ValueError: If query is not a str, Message, or list[Message].
            RuntimeError: If the LLM requests an unregistered tool.

        Example::

            # String query
            response = await client.invoke("Hello!")

            # With message history
            messages = [
                Message(role="system", content="You are helpful"),
                Message(role="user", content="Hi")
            ]
            response = await client.invoke(messages)

            # Override model
            response = await client.invoke("Quick question", model_name="openai/gpt-3.5-turbo")

        Note:
            This method only handles ONE round of tool calling. For multi-step reasoning
            with multiple tool call rounds, use ReactAgent instead.
        """
        if type(query) is str:
            messages = [Message(role="user", content=query)]
        elif type(query) is Message:
            messages = [query]
        elif type(query) is list:
            messages = query
        else:
            raise ValueError("Parameter query is of wrong type!")

        response = await self._make_llm_call(messages, model_name)

        if response.message.tool_calls is not None:
            messages.append(response.message.model_dump())
            for tc in response.message.tool_calls:
                tool_call_id, tool_name, tool_result = await self._make_tool_call(tc)
                print(f"🤖 Called tool {tool_name}")

                tool_message = Message(
                    role="tool",
                    content=tool_result,
                    tool_call_id=tool_call_id,
                    name=tool_name,
                )
                messages.append(tool_message)

            response = await self._make_llm_call(messages, model_name)
        else:
            if verbose:
                print(f"🤖 Response: {response.message.content}")

        return response
