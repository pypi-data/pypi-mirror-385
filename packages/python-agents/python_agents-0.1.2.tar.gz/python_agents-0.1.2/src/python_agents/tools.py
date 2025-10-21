import inspect


def create_tool_schema(func):
    """Add a custom Python function as a tool

    Args:
        func: A Python function to add as a tool
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
    tool_schema = {
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
    """Convert MCP tool format to OpenAI tool format"""
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
