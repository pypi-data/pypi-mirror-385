"""Observability and monitoring configuration schemas.

This module defines Pydantic models for configuring observability and monitoring
capabilities within the Aigency framework. It provides structured configuration
for various monitoring systems and observability tools that help track agent
performance, behavior, and system health.

The observability configuration enables comprehensive monitoring of agent
operations, including metrics collection, logging, tracing, and integration
with external monitoring platforms.

Example:
    Configuring observability settings:

    >>> monitoring = Monitoring(phoenix=Phoenix(enabled=True, metrics_endpoint="/metrics"))
    >>> observability = Observability(
    ...     monitoring=monitoring
    ... )

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel
from aigency.schemas.observability.phoenix import Phoenix


class Monitoring(BaseModel):
    """Configuration for monitoring tools.

    Attributes:
        phoenix (Phoenix): Phoenix monitoring configuration.
    """

    phoenix: Phoenix


class Observability(BaseModel):
    """Groups all observability configurations.

    Attributes:
        monitoring (Monitoring): Monitoring tools configuration.
    """

    monitoring: Monitoring
