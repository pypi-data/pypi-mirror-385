"""REACT agent implementation for step-by-step reasoning and acting.

This module provides the ReactAgent class, which implements the REACT (Reasoning and Acting)
pattern for AI agents. REACT agents combine reasoning about problems with taking actions
(via tool calls) in an iterative loop, continuing until a task is completed or a maximum
number of iterations is reached.
"""

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
    """Agent that uses iterative reasoning and acting (REACT) to solve tasks.

    ReactAgent implements the REACT pattern where the agent follows a loop of:
    1. Reasoning about what to do next
    2. Acting by calling tools to gather information or perform actions
    3. Observing the results
    4. Repeating until the task is complete

    The agent uses a system prompt that guides it to think step-by-step, call tools when
    needed, and provide a final answer when done. The loop continues until the agent
    includes "Final Answer:" in its response or max_iterations is reached.

    Attributes:
        client (LLMClient): The LLM client used to interact with the language model.
            Should have any required tools already registered via add_tool().
        max_iterations (int): Maximum number of reasoning/acting iterations before stopping.
        iteration_count (int): Current iteration number (set during run()).
        task_completed (bool): Whether the agent has completed the task (set during run()).

    Example:
        Basic usage with tools::

            def search_web(query: str) -> str:
                '''Search the web for information.

                Args:
                    query: Search query string

                Returns:
                    Search results as text
                '''
                # Implementation
                return "Search results..."

            client = LLMClient("openai/gpt-4-turbo")
            client.add_tool(search_web)

            agent = ReactAgent(client, max_iterations=5)
            result = await agent.run("What is the capital of France?", verbose=True)
            print(result)  # Will include "Final Answer: Paris"

        With multiple tools and complex reasoning::

            agent = ReactAgent(client, max_iterations=10)
            result = await agent.run(
                "Find the weather in Tokyo and calculate the temperature in Fahrenheit",
                verbose=True
            )
            # Agent will:
            # 1. Think about what tools to use
            # 2. Call weather tool for Tokyo
            # 3. Observe the celsius result
            # 4. Call calculator to convert to Fahrenheit
            # 5. Provide final answer with both values
    """

    def __init__(self, client: LLMClient, max_iterations: int = 10):
        """Initialize a ReactAgent.

        Args:
            client (LLMClient): The LLM client to use. Tools should be registered
                on this client before creating the agent.
            max_iterations (int, optional): Maximum number of reasoning iterations
                before stopping. Prevents infinite loops. Defaults to 10.
        """
        self.client = client
        self.max_iterations = max_iterations

    def _is_task_completed(self, response) -> bool:
        """Check if the agent has completed the task.

        Internal method that determines if the task is done by looking for
        "Final Answer:" in the response content. This is the signal that the
        agent has gathered all necessary information and is providing its final result.

        Args:
            response: The response object from the LLM containing the message.

        Returns:
            bool: True if "Final Answer:" appears in the response content, False otherwise.
        """
        return "Final Answer:" in response.message.content

    async def run(self, task: str, verbose: bool = False):
        """Run the agent on a task using iterative reasoning and acting.

        This method executes the REACT loop: the agent reasons about the task, calls tools
        as needed, observes results, and repeats until it provides a final answer or reaches
        max_iterations. The conversation history is maintained across iterations, with the
        REACT system prompt prepended to guide the agent's behavior.

        Args:
            task (str): The task or question for the agent to solve. Should be a clear
                description of what you want the agent to accomplish.
            verbose (bool, optional): If True, prints iteration numbers and agent responses
                to stdout for debugging. Defaults to False.

        Returns:
            str: The final response from the agent, which should include "Final Answer:"
                followed by the result. If max_iterations is reached before completion,
                returns the last response received.

        Example::

            # Simple task
            agent = ReactAgent(client)
            result = await agent.run("What is 25 * 4?")

            # Complex task with verbose output
            result = await agent.run(
                "Research the population of New York City and compare it to Los Angeles",
                verbose=True
            )
            # Prints iteration progress and all agent reasoning steps

        Note:
            - The agent's iteration_count and task_completed attributes are set during execution
            - If the agent doesn't complete within max_iterations, task_completed will be False
            - All conversation history (including tool calls and results) is maintained throughout
            - The REACT system prompt is automatically added as the first message
        """
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
