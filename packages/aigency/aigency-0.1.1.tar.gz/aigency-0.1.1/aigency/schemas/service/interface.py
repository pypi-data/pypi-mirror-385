"""Service interface configuration schema.

This module defines the Interface Pydantic model for configuring service
interfaces within the Aigency framework. It provides structured configuration
for defining how services expose their functionality and communicate with
other components in the system.

The interface configuration establishes the communication protocols, endpoints,
and interaction patterns that services use to integrate with the broader
agent ecosystem.

Example:
    Configuring service interface:

    >>> interface = Interface(
    ...     default_input_modes=["text/plain"],
    ...     default_output_modes=["text/plain"]
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from typing import List
from pydantic import BaseModel


class Interface(BaseModel):
    """Define the agent's communication modes.

    Attributes:
        default_input_modes (List[str]): List of supported input communication modes.
        default_output_modes (List[str]): List of supported output communication modes.
    """

    default_input_modes: List[str]
    default_output_modes: List[str]
