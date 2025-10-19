"""Remote agent connection configuration schema.

This module defines the RemoteAgent Pydantic model for configuring connections
to remote agents in the Aigency framework. It provides the necessary structure
for establishing communication with agents running on different services or
locations within the A2A ecosystem.

The RemoteAgent configuration enables agents to discover and communicate with
other agents, facilitating distributed agent architectures and collaborative
agent workflows.

Example:
    Configuring a remote agent connection:

    >>> remote_agent = RemoteAgent(
    ...     name="data_processor",
    ...     host="agent-data-processor",
    ...     port=8080
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel, Field


class RemoteAgent(BaseModel):
    """Remote agent configuration.

    Configuration for connecting to remote agents in the A2A protocol.

    Attributes:
        name (str): Name identifier for the remote agent.
        host (str): Hostname or IP address of the remote agent.
        port (int): Port number for the remote agent connection (1-65535).
    """

    name: str
    host: str
    port: int = Field(..., ge=1, le=65535)
