"""Agent metadata and descriptive information schema.

This module defines the Metadata Pydantic model for storing descriptive information
about agents in the Aigency framework. It provides structured metadata that helps
identify, categorize, and describe agents within the system.

The metadata includes essential information such as agent names, descriptions,
versions, and other descriptive attributes that facilitate agent discovery,
management, and documentation.

Example:
    Creating agent metadata:

    >>> metadata = Metadata(
    ...     name="data_analyst",
    ...     description="Analyzes data and generates reports",
    ...     version="1.0.0",
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel


class Metadata(BaseModel):
    """Descriptive metadata of the agent.

    Attributes:
        name (str): Name of the agent.
        version (str): Version identifier of the agent.
        description (str): Human-readable description of the agent's purpose.
    """

    name: str
    version: str
    description: str
