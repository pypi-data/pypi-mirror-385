"""Tool schema generation and conversion utilities.

This module provides utilities for converting Python functions and MCP tools
into OpenAI-compatible tool schemas. It handles automatic schema generation
through function introspection, extracting type information from annotations
and documentation from docstrings.
"""

import inspect
from typing import Any, Callable, TypedDict


class ParameterSchema(TypedDict):
    type: str
    description: str | None
    default: Any | None


class ToolFunctionSchema(TypedDict):
    name: str
    description: str
    parameters: dict[str, ParameterSchema] | dict[str, Any]


class ToolSchema(TypedDict):
    type: str
    function: ToolFunctionSchema


def create_tool_schema(func: Callable[..., Any]) -> ToolSchema:
    """Generate an OpenAI tool schema from a Python function.

    This function uses introspection to automatically create a tool schema in OpenAI's
    function calling format. It extracts parameter information from the function signature,
    including type hints and default values, and uses the function's docstring as the
    tool description.

    Type mapping:
        - int → "integer"
        - float → "number"
        - str → "string"
        - bool → "boolean"
        - Other types → "string" (default)

    Parameters without default values are marked as required in the schema.

    Args:
        func (callable): A Python function to convert into a tool schema. Should have
            type hints for parameters and a descriptive docstring.

    Returns:
        dict: A tool schema in OpenAI format with structure::

            {
                "type": "function",
                "function": {
                    "name": str,
                    "description": str,
                    "parameters": {
                        "type": "object",
                        "properties": dict,
                        "required": list[str]
                    }
                }
            }

    Example:
        Converting a simple function to a tool schema::

            def add_numbers(a: int, b: int) -> int:
                '''Add two numbers together.'''
                return a + b

            schema = create_tool_schema(add_numbers)
            # Returns:
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "add_numbers",
            #         "description": "Add two numbers together.",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "a": {"type": "integer"},
            #                 "b": {"type": "integer"}
            #             },
            #             "required": ["a", "b"]
            #         }
            #     }
            # }

        With optional parameters::

            def greet(name: str, greeting: str = "Hello") -> str:
                '''Greet someone with a custom message.'''
                return f"{greeting}, {name}!"

            schema = create_tool_schema(greet)
            # required list will only contain ["name"]
    """
    sig = inspect.signature(func)
    func_name = func.__name__
    # Extract parameters from function signature
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        # Determine type from annotation or default to string
        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            type_map = {
                int: "integer",
                float: "number",
                str: "string",
                bool: "boolean",
            }
            param_type = type_map.get(param.annotation, "string")

            properties[param_name] = {"type": param_type}

        # Mark as required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    # Get description from docstring
    description = func.__doc__ or f"Custom tool: {func_name}"
    description = description.strip()

    # Create OpenAI tool format schema
    tool_schema: ToolSchema = {
        "type": "function",
        "function": {
            "name": func_name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }

    return tool_schema


def convert_tool_format(tool):
    """Convert an MCP tool to OpenAI tool format.

    This function transforms tools from the Model Context Protocol (MCP) format
    into OpenAI's function calling schema format. It maps the MCP tool's inputSchema
    directly to OpenAI's parameters structure.

    Args:
        tool: An MCP tool object with the following attributes:

            - name (str): The tool's name
            - description (str): Description of what the tool does
            - inputSchema (dict): JSON schema for the tool's input parameters,
              containing "properties" and optionally "required" fields

    Returns:
        dict: A tool schema in OpenAI format with structure::

            {
                "type": "function",
                "function": {
                    "name": str,
                    "description": str,
                    "parameters": {
                        "type": "object",
                        "properties": dict,
                        "required": list[str]
                    }
                }
            }

    Example:
        Converting an MCP tool::

            from types import SimpleNamespace

            mcp_tool = SimpleNamespace(
                name="search_database",
                description="Search the database for records",
                inputSchema={
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer"}
                    },
                    "required": ["query"]
                }
            )

            openai_tool = convert_tool_format(mcp_tool)
            # Returns OpenAI-compatible tool schema

    Note:
        If the MCP tool's inputSchema doesn't specify a "required" field,
        an empty list is used for the required parameters.
    """
    converted_tool = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"],
                "required": tool.inputSchema.get("required", []),
            },
        },
    }
    return converted_tool
