"""Agent core logic and capabilities schema definition.

This module defines the Agent Pydantic model that represents the core logic,
AI model configuration, and capabilities of an Aigency agent. It serves as
the central configuration for an agent's behavior, skills, tools, and
communication capabilities with other agents.

The Agent class encapsulates all the essential components needed to define
an intelligent agent including its instruction set, model configuration,
available skills, tools, and connections to remote agents.

Example:
    Creating an agent configuration:

    >>> agent = Agent(
    ...     model=AgentModel(name="gpt-4", provider="openai"),
    ...     instruction="You are a helpful assistant",
    ...     skills=[Skill(name="math", description="Mathematical operations")],
    ...     tools=[Tool(name="calculator", type=ToolType.FUNCTION)]
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel
from typing import List, Optional
from aigency.schemas.agent.model import AgentModel
from aigency.schemas.agent.skills import Skill
from aigency.schemas.agent.tools import Tool
from aigency.schemas.agent.remote_agent import RemoteAgent


class Agent(BaseModel):
    """The agent's 'brain': its logic, model and capabilities.

    Attributes:
        model (AgentModel): Configuration for the AI model to use.
        instruction (str): System instruction that defines the agent's behavior.
        skills (List[Skill]): List of skills the agent possesses.
        tools (List[Tool], optional): List of tools available to the agent.
        remote_agents (List[RemoteAgent], optional): List of remote agents this
            agent can communicate with.
    """

    model: AgentModel
    instruction: str
    skills: List[Skill]
    tools: Optional[List[Tool]] = []
    remote_agents: Optional[List[RemoteAgent]] = []
