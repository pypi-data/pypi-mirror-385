"""Agent executor module for A2A integration.

This module provides the execution engine for agents within the A2A (Agent-to-Agent)
protocol framework. It handles the lifecycle of agent tasks, session management,
and integration with Google ADK runners for processing agent requests.

The AgentA2AExecutor class manages the execution flow from task submission through
completion, handling streaming responses, function calls, and error conditions
while maintaining compatibility with the A2A protocol specifications.

Example:
    Creating and using an agent executor:

    >>> runner = Runner(app_name="my_agent", agent=agent)
    >>> executor = AgentA2AExecutor(runner, agent_card)
    >>> await executor.execute(context, event_queue)

Attributes:
    logger: Module-level logger instance for execution events.
    DEFAULT_USER_ID (str): Default user identifier for session management.

Todo:
    * Replace DEFAULT_USER_ID with proper user management system.
"""

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCard, TaskState, UnsupportedOperationError
from a2a.utils.errors import ServerError
from google.adk.runners import Runner
from google.genai import types

from aigency.utils.logger import get_logger
from aigency.utils.utils import (
    convert_a2a_part_to_genai,
    convert_genai_part_to_a2a,
)

logger = get_logger()

# TODO: This needs to be changed
DEFAULT_USER_ID = "self"


class AgentA2AExecutor(AgentExecutor):
    """Agent executor for A2A integration with Google ADK runners.

    This class handles the execution of agent tasks within the A2A protocol,
    managing sessions, processing requests, and handling task lifecycle.

    Attributes:
        _card (AgentCard): The agent card containing metadata about the agent.
        _active_sessions (set[str]): Set of active session IDs for tracking.
        runner (Runner): The Google ADK runner instance for executing agent logic.
    """

    def __init__(self, runner: Runner, card: AgentCard):
        """Initialize the BaseAgentA2AExecutor.

        Args:
            runner (Runner): The Google ADK runner instance.
            card (AgentCard): The agent card containing metadata about the agent.
        """
        self._card = card
        # Track active sessions for potential cancellation
        self._active_sessions: set[str] = set()
        self.runner = runner

    async def _upsert_session(self, session_id: str) -> "Session":
        """Retrieve a session if it exists, otherwise create a new one.

        Ensures that async session service methods are properly awaited.

        Args:
            session_id (str): The ID of the session to retrieve or create.

        Returns:
            Session: The retrieved or newly created session object.
        """
        logger.info("session_id: %s", session_id)
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
        )
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
            )
        return session

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        """Process a request through the agent runner.

        Args:
            new_message (types.Content): The message content to process.
            session_id (str): The session ID for this request.
            task_updater (TaskUpdater): Task updater for reporting progress.
        """
        session_obj = await self._upsert_session(session_id)
        session_id = session_obj.id

        self._active_sessions.add(session_id)

        try:
            async for event in self.runner.run_async(
                session_id=session_id,
                user_id=DEFAULT_USER_ID,
                new_message=new_message,
            ):
                if event.is_final_response():
                    parts = []
                    if event.content:
                        parts = [
                            convert_genai_part_to_a2a(part)
                            for part in event.content.parts
                            if (part.text or part.file_data or part.inline_data)
                        ]
                    logger.debug("Yielding final response: %s", parts)
                    await task_updater.add_artifact(parts)
                    await task_updater.update_status(TaskState.completed, final=True)
                    break
                if not event.get_function_calls():
                    logger.debug("Yielding update response")
                    message_parts = []
                    if event.content:
                        message_parts = [
                            convert_genai_part_to_a2a(part)
                            for part in event.content.parts
                            if (part.text)
                        ]
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(message_parts),
                    )
                else:
                    logger.debug("Skipping event")
        finally:
            # Remove from active sessions when done
            self._active_sessions.discard(session_id)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        """Execute an agent task.

        Args:
            context (RequestContext): The request context containing task information.
            event_queue (EventQueue): Event queue for task updates.
        """
        # Run the agent until either complete or the task is suspended.
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        # Immediately notify that the task is submitted.
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)
        await self._process_request(
            types.UserContent(
                parts=[
                    convert_a2a_part_to_genai(part) for part in context.message.parts
                ],
            ),
            context.context_id,
            updater,
        )

        logger.debug("[ADKAgentA2AExecutor] execute exiting")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel an active agent task.

        Args:
            context (RequestContext): The request context for the task to cancel.
            event_queue (EventQueue): Event queue for task updates.

        Raises:
            ServerError: Always raised as cancellation is not currently supported.
        """
        session_id = context.context_id
        if session_id in self._active_sessions:
            logger.info("Cancellation requested for active session: %s", session_id)
            self._active_sessions.discard(session_id)
        else:
            logger.debug("Cancellation requested for inactive session: %s", session_id)

        raise ServerError(error=UnsupportedOperationError())
