"""Memory management for conversation history in agents.

This module provides abstract and concrete implementations for storing and managing
conversation history (messages) in AI agents. Memory classes handle message storage,
retrieval, and manipulation for maintaining context across agent interactions.
"""

from abc import ABC, abstractmethod

from python_agents.message import Message


class BaseMemory(ABC):
    """Abstract base class for memory implementations.

    BaseMemory defines the interface that all memory implementations must follow.
    It provides methods for adding messages, clearing history, and managing system messages.
    Subclasses must implement all abstract methods to provide specific storage strategies.
    """

    @abstractmethod
    def add_message(self, message: Message):
        """Add a message to the conversation history.

        Args:
            message (Message): The message to add to memory. Should contain role, content,
                and optionally tool call information.
        """
        pass

    @abstractmethod
    def clear(self):
        """Clear all messages from memory.

        Removes all stored messages, resetting the conversation history to empty state.
        """
        pass

    @abstractmethod
    def insert_system_message(self, message: Message):
        """Insert or replace a system message at the beginning of conversation history.

        System messages provide instructions or context to the LLM and should always
        appear first in the message list. This method either inserts a new system message
        or replaces an existing one.

        Args:
            message (Message): The system message to insert. Should have role="system".
        """
        pass


class SimpleMemory(BaseMemory):
    """Simple in-memory storage for conversation history.

    SimpleMemory provides a basic list-based implementation of conversation history storage.
    Messages are stored in chronological order in a Python list, with no size limits or
    special processing. This implementation is suitable for most use cases where conversation
    history fits in memory.

    Attributes:
        messages (list[Message]): List of messages in chronological order.

    Example:
        Basic usage with message storage::

            memory = SimpleMemory()
            memory.add_message(Message(role="user", content="Hello"))
            memory.add_message(Message(role="assistant", content="Hi there!"))
            print(len(memory.messages))  # 2
            memory.clear()
            print(len(memory.messages))  # 0
    """

    def __init__(self):
        """Initialize an empty SimpleMemory instance."""
        self.messages = []

    def add_message(self, message: Message):
        """Add a message to the end of the conversation history.

        Messages are appended in the order they are added, maintaining chronological order.

        Args:
            message (Message): The message to add. Can be user, assistant, system, or tool message.
        """
        self.messages.append(message)

    def insert_system_message(self, message: Message):
        """Insert or replace the system message at the beginning of the conversation.

        This method ensures the system message is always first in the message list.
        If a system message already exists at position 0, it is replaced. Otherwise,
        the new system message is inserted at the beginning.

        Args:
            message (Message): The system message to insert. Should have role="system".

        Note:
            System messages provide instructions or context to the LLM and must appear
            before any user or assistant messages to be effective.
        """
        if len(self.messages) > 0:
            if self.messages[0]["role"] == "system":
                self.messages[0] = message
            else:
                self.messages.insert(0, message)
        else:
            self.messages = [message]

    def clear(self):
        """Clear all messages from memory.

        Resets the conversation history to an empty state by clearing the messages list.
        """
        self.messages = []
