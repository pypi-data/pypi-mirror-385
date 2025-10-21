import json

from openai import AsyncOpenAI

from python_agents import tools, utils
from python_agents.memory import BaseMemory
from python_agents.message import Message


class LLMClient:
    def __init__(
        self,
        model_name: str = None,
        base_url: str = "https://openrouter.ai/api/v1",
        memory: BaseMemory = None,
    ):
        self.model_name = model_name
        self.client = AsyncOpenAI(base_url=base_url)
        self.memory = memory
        self.tools = {}

    def add_tool(self, func):
        schema = tools.create_tool_schema(func)
        self.tools[func.__name__] = {"func": func, "schema": schema}

    async def _make_llm_call(self, messages: list[Message], model_name: str = None):
        available_tools = [tool["schema"] for tool in self.tools.values()]

        utils.pretty_print(messages)

        response = await self.client.chat.completions.create(
            model=model_name or self.model_name,
            messages=messages,
            tools=available_tools,
        )

        return response.choices[0]

    async def _make_tool_call(self, tc):
        tool_name = tc.function.name
        tool_args = tc.function.arguments
        tool_args = json.loads(tool_args) if tool_args else {}

        if tool_name in self.tools:
            func = self.tools[tool_name]["func"]
            tool_result = str(func(**tool_args))
        else:
            raise RuntimeError(f"LLM tried to call unknown tool '{tool_name}'")
        return tc.id, tool_name, tool_result

    async def invoke(self, message: Message | str, model_name=None):
        if type(message) is str:
            message = Message(role="user", content=message)

        if self.memory:
            self.memory.add_message(message)

        messages = self.memory.messages.copy() if self.memory else [message]
        response = await self._make_llm_call(messages, model_name)

        if self.memory:
            msg = Message(role=response.message.role, content=response.message.content)
            self.memory.add_message(msg)

        if response.message.tool_calls is not None:
            messages.append(response.message.model_dump())
            if self.memory:
                self.memory.add_message(Message(response.message.model_dump()))
            for tc in response.message.tool_calls:
                tool_call_id, tool_name, tool_result = await self._make_tool_call(tc)

                tool_message = Message(
                    role="tool",
                    content=tool_result,
                    tool_call_id=tool_call_id,
                    name=tool_name,
                )
                messages.append(tool_message)
                if self.memory:
                    self.memory.add_message(tool_message)

            response = await self._make_llm_call(messages, model_name)
            if self.memory:
                self.memory.add_message(Message(role="assistant", content=response.message.content))

        return response
