"""Utility functions for the python-agents library.

This module provides helper functions for common tasks like formatting and displaying
data structures in a human-readable format.
"""

import json


def pretty_print(data: dict):
    """Print a dictionary in a formatted, human-readable JSON format.

    This utility function converts a dictionary to JSON and prints it with sorted keys
    and 4-space indentation, making it easier to read complex nested data structures.
    Commonly used for debugging or displaying API responses, message histories, and
    tool call results.

    Args:
        data (dict): The dictionary to print. Can contain nested dictionaries, lists,
            strings, numbers, booleans, and None values - any JSON-serializable types.

    Example:
        Displaying simple data::

            data = {"name": "Alice", "age": 30, "city": "Paris"}
            pretty_print(data)
            # Output:
            # {
            #     "age": 30,
            #     "city": "Paris",
            #     "name": "Alice"
            # }

        Displaying nested conversation messages::

            message = {
                "role": "assistant",
                "content": "Hello!",
                "metadata": {
                    "model": "gpt-4",
                    "tokens": 5
                }
            }
            pretty_print(message)
            # Output:
            # {
            #     "content": "Hello!",
            #     "metadata": {
            #         "model": "gpt-4",
            #         "tokens": 5
            #     },
            #     "role": "assistant"
            # }

        Displaying tool call information::

            tool_call = {
                "id": "call_abc123",
                "function": {
                    "name": "get_weather",
                    "arguments": {"location": "Tokyo"}
                }
            }
            pretty_print(tool_call)

    Note:
        - Keys are automatically sorted alphabetically for consistent output
        - Uses 4-space indentation for readability
        - Non-JSON-serializable objects will raise a TypeError
        - Output is printed directly to stdout, not returned
    """
    print(json.dumps(data, sort_keys=True, indent=4))
