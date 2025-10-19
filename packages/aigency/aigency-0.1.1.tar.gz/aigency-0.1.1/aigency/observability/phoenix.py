"""Phoenix observability integration module.

This module provides Phoenix monitoring and observability integration for the
Aigency framework. Phoenix is an open-source observability platform that enables
comprehensive monitoring, tracing, and analysis of AI agent behavior and performance.

The Phoenix integration automatically instruments agent operations to provide
insights into model calls, token usage, latency metrics, and execution traces.
This enables developers to monitor agent performance, debug issues, and optimize
agent behavior in production environments.

Example:
    Configuring Phoenix monitoring:

    >>> from aigency.schemas.observability.phoenix import Phoenix as PhoenixConfig
    >>> config = PhoenixConfig(host="phoenix", port=6006, project_name="my_agent")
    >>> phoenix = Phoenix(config)

Attributes:
    None: This module contains only the Phoenix integration class.
"""

from phoenix.otel import register
from aigency.utils.singleton import Singleton
from aigency.schemas.observability.phoenix import Phoenix as PhoenixConfig


class Phoenix(Singleton):
    """Phoenix observability integration for agent monitoring.

    This class provides a singleton interface to Phoenix observability platform,
    enabling automatic instrumentation and tracing of agent operations. It handles
    the registration of OpenTelemetry tracing with Phoenix endpoints and manages
    the lifecycle of observability data collection.

    The Phoenix integration captures detailed telemetry data including:
    - Model inference calls and responses
    - Token usage and costs
    - Execution latency and performance metrics
    - Error tracking and debugging information

    Attributes:
        config (PhoenixConfig): Phoenix configuration containing host, port, and project settings.
        tracer_provider: OpenTelemetry tracer provider for Phoenix integration.

    Example:
        >>> config = PhoenixConfig(host="localhost", port=6006, project_name="agent_project")
        >>> phoenix = Phoenix(config)
    """

    def __init__(self, config: PhoenixConfig):
        """Initialize Phoenix observability integration.

        Args:
            config (PhoenixConfig): Configuration object containing Phoenix connection
                settings including host, port, and project name.

        Raises:
            ConnectionError: If unable to connect to Phoenix endpoint.
            ValueError: If configuration parameters are invalid.
        """
        self.config = config
        self.tracer_provider = register(
            endpoint=f"http://{self.config.host}:{self.config.port}/v1/traces",
            project_name=self.config.project_name,
            auto_instrument=True
        )