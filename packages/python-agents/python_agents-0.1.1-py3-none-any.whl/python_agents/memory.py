from python_agents.message import Message


class BaseMemory:
    pass


class SimpleMemory(BaseMemory):
    def __init__(self):
        self.messages = []

    def add_message(self, message: Message):
        self.messages.append(message)
