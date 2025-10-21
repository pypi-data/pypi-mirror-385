from python_agents.client import LLMClient
from python_agents.message import Message


REACT_PROMPT_TEMPLATE = """You are an AI assistant that uses a step-by-step reasoning approach to solve problems.

You have access to tools through function calling. When you need information or to perform an action, call the appropriate tool function.

Follow this reasoning pattern:

1. **Think** about what you need to do
2. **Call tools** to gather information or perform actions (use function calling)
3. **Observe** the results and think about the next step
4. **Repeat** until you have enough information
5. **Provide Final Answer** when the task is complete

IMPORTANT RULES:
- You MUST start each step by explaining your reasoning (what you're thinking)
- When you need information, call the appropriate tool function directly
- After receiving tool results, analyze them and decide what to do next
- Be specific and clear in your reasoning
- When you have completed the task or gathered all necessary information, start your response with "Final Answer:" followed by a complete summary
- Don't make up information - always use the available tools to get accurate data
- The "Final Answer:" signals you are done and should contain a complete response to the original task

Remember: Reason step-by-step, use tools when needed, and clearly indicate when you're providing your final answer."""


class ReactAgent:
    def __init__(self, client: LLMClient, max_iterations: int = 10):
        self.client = client
        self.max_iterations = max_iterations

    def _is_task_completed(self, response) -> bool:
        return "Final Answer:" in response.message.content

    async def run(self, task: str, verbose: bool = False):
        self.iteration_count = 0
        self.task_completed = False

        final_response = ""
        history = [
            Message(role="system", content=REACT_PROMPT_TEMPLATE),
            Message(role="user", content=task),
        ]
        while not self.task_completed and self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            if verbose:
                print(f"-- Iteration: {self.iteration_count} / {self.max_iterations} --")

            response = await self.client.invoke(history)
            history.append(Message(role=response.message.role, content=response.message.content))
            if verbose:
                print(response.message.content)

            final_response = response.message.content

            if self._is_task_completed(response):
                self.task_completed = True

        return final_response
