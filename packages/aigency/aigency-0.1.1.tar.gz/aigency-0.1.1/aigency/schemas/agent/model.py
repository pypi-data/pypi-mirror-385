"""AI model configuration schemas for agent setup.

This module defines Pydantic models for configuring AI models and their providers
within the Aigency framework. It provides structured configuration for different
AI model providers and their specific parameters, enabling flexible model
selection and configuration for agents.

The models support various AI providers and allow for extensible configuration
of model-specific parameters, API keys, and other provider-specific settings.

Example:
    Creating model configurations:

    >>> provider_config = ProviderConfig(name="openai", endpoint="https://api.openai.com")
    >>> model = AgentModel(name="gpt-4", provider=provider_config)

Attributes:
    None: This module contains only Pydantic model definitions.
"""

from typing import Optional
from pydantic import BaseModel


class ProviderConfig(BaseModel):
    """Configuration for AI model provider.

    Attributes:
        name (str): Name of the AI provider.
        endpoint (str, optional): Custom endpoint URL for the provider.
    """

    name: str
    api_base: Optional[str] = None


class AgentModel(BaseModel):
    """Configuration for AI model.

    Attributes:
        name (str): Name of the AI model to use.
        provider (ProviderConfig, optional): Provider configuration details.
    """

    name: str
    provider: Optional[ProviderConfig] = None
