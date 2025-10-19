"""Service network and communication configuration schema.

This module defines the Service Pydantic model for configuring service-level
settings within the Aigency framework. It provides structured configuration
for network communication, service discovery, and integration parameters
that enable agents to operate as distributed services.

The service configuration encompasses network settings, communication protocols,
and service-specific parameters that facilitate agent deployment and operation
in distributed environments.

Example:
    Configuring service settings:

    >>> service = Service(
    ...     interface=Interface(default_input_modes=["text/plain"]),
    ...     capabilities=Capabilities(streaming=True),
    ...     host="0.0.0.0",
    ...     port=8080
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel
from aigency.schemas.service.interface import Interface
from aigency.schemas.service.capabilities import Capabilities


class Service(BaseModel):
    """Network and communication configuration of the agent.

    Attributes:
        url (str): Base URL where the agent service is accessible.
        interface (Interface): Communication interface configuration.
        capabilities (Capabilities): Technical capabilities of the service.
    """

    url: str
    interface: Interface
    capabilities: Capabilities
