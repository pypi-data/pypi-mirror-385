"""Agent skill definition and configuration schema.

This module defines the Skill Pydantic model for representing specific capabilities
or skills that an agent possesses within the Aigency framework. Skills define
what an agent can do and provide structured metadata about the agent's abilities.

Skills serve as descriptive components that help categorize and communicate an
agent's capabilities to other agents and systems in the A2A ecosystem.

Example:
    Defining agent skills:

    >>> skill = Skill(
    ...     name="data_analysis",
    ...     description="Analyze datasets and generate insights",
    ...     tags=["analytics"]
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel
from typing import List


class Skill(BaseModel):
    """Define a specific skill of the agent.

    Attributes:
        id (str): Unique identifier for the skill.
        name (str): Human-readable name of the skill.
        description (str): Detailed description of what the skill does.
        tags (List[str]): List of tags for categorizing the skill.
        examples (List[str]): List of usage examples for the skill.
    """

    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]
