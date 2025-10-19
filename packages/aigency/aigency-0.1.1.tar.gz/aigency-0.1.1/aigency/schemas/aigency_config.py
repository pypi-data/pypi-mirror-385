"""Root configuration model for Aigency agents.

This module defines the main configuration schema for Aigency agents using Pydantic
models. It provides a comprehensive structure that encompasses all aspects of agent
configuration including metadata, service settings, agent logic, and observability.

The AigencyConfig class serves as the root model that validates and structures
agent configurations loaded from YAML files, ensuring type safety and proper
validation of all configuration parameters.

Example:
    Loading and using agent configuration:

    >>> config_data = yaml.safe_load(open("agent.yaml"))
    >>> config = AigencyConfig(**config_data)
    >>> agent_name = config.metadata.name
    >>> model_name = config.agent.model.name

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from pydantic import BaseModel
from typing import Optional
from aigency.schemas.observability.observability import Observability
from aigency.schemas.metadata.metadata import Metadata
from aigency.schemas.agent.agent import Agent
from aigency.schemas.service.service import Service


class AigencyConfig(BaseModel):
    """Root Pydantic model for complete agent configuration.

    This is the main configuration model that encompasses all aspects of an
    agent's setup including metadata, service configuration, agent logic,
    and observability settings.

    Attributes:
        metadata (Metadata): Descriptive information about the agent.
        service (Service): Network and communication configuration.
        agent (Agent): Core agent logic, model, and capabilities.
        observability (Observability, optional): Monitoring and observability settings.
    """

    metadata: Metadata
    service: Service
    agent: Agent
    observability: Optional[Observability] = None
