"""Phoenix monitoring system configuration schema.

This module defines the Phoenix Pydantic model for configuring Phoenix monitoring
integration within the Aigency framework. Phoenix is a monitoring and observability
platform that provides insights into agent behavior, performance metrics, and
system health monitoring.

The Phoenix configuration enables agents to integrate with Phoenix monitoring
services, allowing for comprehensive tracking and analysis of agent operations
in production environments.

Example:
    Configuring Phoenix monitoring:

    >>> phoenix = Phoenix(
    ...     host="phoenix",
    ...     port=6006,
    ...     project_name="demo"
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel


class Phoenix(BaseModel):
    """Configuration for Phoenix monitor.

    Attributes:
        host (str): Hostname or IP address for Phoenix monitoring service.
        port (int): Port number for Phoenix monitoring service.
        project_name (str): Name of the project for Phoenix monitoring.
    """

    host: str
    port: int
    project_name: str
