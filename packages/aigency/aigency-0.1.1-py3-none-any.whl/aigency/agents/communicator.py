"""Agent-to-Agent communication module.

This module provides the core communication infrastructure for agents to interact
with each other using the A2A (Agent-to-Agent) protocol. It handles message
creation, payload formatting, and remote agent connection management.

The main component is the Communicator class which manages connections to remote
agents and provides methods for delegating tasks and sending messages between
agents in a distributed system.

Example:
    Basic usage for agent communication:

    >>> connections = {"agent1": client1, "agent2": client2}
    >>> communicator = Communicator(connections)
    >>> task_result = await communicator.send_message("agent1", "task description", context)

Attributes:
    logger: Module-level logger instance for communication events.
"""

import uuid
from typing import Any, Awaitable

from a2a.types import Message, Task
from google.adk.tools.tool_context import ToolContext

from aigency.utils.logger import get_logger

logger = get_logger()


class Communicator:
    """Base class for agent-to-agent communication.

    This class manages connections to remote agents and provides methods for
    sending messages and delegating tasks to them.

    Attributes:
        remote_agent_connections (dict[str, Any]): Dictionary mapping agent names
            to their client connection objects.
    """

    def __init__(self, remote_agent_connections: dict[str, Any] | None = None):
        """Initialize the communicator with remote agent connections.

        Args:
            remote_agent_connections (dict[str, Any] | None, optional): A dictionary
                that maps agent names to their client connection objects.
                Defaults to None.
        """
        self.remote_agent_connections: dict[str, Any] = remote_agent_connections or {}

    async def send_message(
        self, agent_name: str, task: str, tool_context: ToolContext
    ) -> Awaitable[Task | None]:
        """Delegate a task to a specific remote agent.

        This method sends a message to a remote agent, requesting it to perform a
        task. It handles message payload creation and communication.

        Args:
            agent_name (str): Name of the remote agent to send the task to.
            task (str): Detailed description of the task for the remote agent.
            tool_context (ToolContext): Context object containing state and other
                information.

        Returns:
            Task | None: A Task object if communication is successful, or None
                otherwise.

        Raises:
            ValueError: If the specified agent is not found in connections.
        """
        logger.info(
            f"`send_message` started for agent: '{agent_name}' with task: '{task}'"
        )
        client = self.remote_agent_connections.get(agent_name)
        if not client:
            available_agents = list(self.remote_agent_connections.keys())
            logger.error(
                f"The LLM tried to call '{agent_name}', but it was not found. "
                f"Available agents: {available_agents}"
            )
            raise ValueError(
                f"Agent '{agent_name}' not found. Available agents: {available_agents}"
            )

        state = tool_context.state

        contexts = state.setdefault("remote_agent_contexts", {})
        agent_context = contexts.setdefault(
            agent_name, {"context_id": str(uuid.uuid4())}
        )
        context_id = agent_context["context_id"]

        task_id = state.get("task_id")
        input_metadata = state.get("input_message_metadata", {})
        message_id = input_metadata.get("message_id")

        payload = self.create_send_message_payload(
            text=task, task_id=task_id, context_id=context_id, message_id=message_id
        )
        logger.debug("`send_message` with the following payload: %s", payload)

        send_response = None

        async for resp in client.send_message(
            message_request=Message(**payload["message"])
        ):
            send_response = resp

        if isinstance(send_response, tuple):
            send_response, _ = send_response

        if not isinstance(send_response, Task):
            logger.warning(
                f"The response received from agent '{agent_name}' is not a Task object. "
                f"Received type: {type(send_response)}"
            )
            return None

        return send_response

    @staticmethod
    def create_send_message_payload(
        text: str,
        task_id: str | None = None,
        context_id: str | None = None,
        message_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a message payload to send to a remote agent.

        Args:
            text (str): The text content of the message.
            task_id (str | None, optional): Task ID to associate with the message.
                Defaults to None.
            context_id (str | None, optional): Context ID to associate with the
                message. Defaults to None.
            message_id (str | None, optional): Message ID. If None, a new one will
                be generated. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary containing the formatted message payload.
        """
        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": text}],
                "message_id": message_id or uuid.uuid4().hex,
            },
        }
        if task_id:
            payload["message"]["task_id"] = task_id
        if context_id:
            payload["message"]["context_id"] = context_id
        return payload
