"""Observability and monitoring orchestration module.

This module provides the central orchestration layer for observability and monitoring
capabilities within the Aigency framework. It manages the initialization and lifecycle
of various monitoring tools and observability platforms that track agent performance,
behavior, and system health.

The Observability class serves as a unified interface for configuring and managing
multiple monitoring systems simultaneously, enabling comprehensive visibility into
agent operations across different environments and deployment scenarios.

Example:
    Initializing observability with agent configuration:

    >>> from aigency.schemas.aigency_config import AigencyConfig
    >>> config = AigencyConfig.from_yaml("agent_config.yaml")
    >>> observability = Observability(config)

Attributes:
    None: This module contains only the Observability orchestration class.
"""

import os
from aigency.observability.phoenix import Phoenix
from aigency.utils.singleton import Singleton
from aigency.schemas.aigency_config import AigencyConfig


class Observability(Singleton):
    """Central orchestration for agent observability and monitoring.

    This singleton class manages the initialization and coordination of various
    observability tools and monitoring platforms. It provides a unified interface
    for configuring multiple monitoring systems based on agent configuration,
    ensuring consistent observability across different deployment environments.

    The class handles the lifecycle management of monitoring integrations and
    provides safe initialization with proper error handling for optional
    observability configurations.

    Attributes:
        aigency_config (AigencyConfig): The agent configuration containing observability settings.
        phoenix (Phoenix, optional): Phoenix monitoring integration instance, if configured.

    Example:
        >>> config = AigencyConfig.from_yaml("agent_config.yaml")
        >>> obs = Observability(config)
        >>> # Phoenix monitoring automatically initialized if configured
    """

    def __init__(self, aigency_config: AigencyConfig):
        """Initialize observability orchestration with agent configuration.

        Args:
            aigency_config (AigencyConfig): Agent configuration object containing
                observability and monitoring settings.

        Note:
            Observability components are initialized only if their respective
            configurations are present and valid. Missing configurations are
            handled gracefully without raising errors.
        """
        self.aigency_config = aigency_config
        self.phoenix = None
        
        if hasattr(aigency_config, 'observability') and aigency_config.observability:
            monitoring = aigency_config.observability.monitoring
            
            if monitoring and hasattr(monitoring, 'phoenix') and monitoring.phoenix:
                self.phoenix = Phoenix(monitoring.phoenix)
    