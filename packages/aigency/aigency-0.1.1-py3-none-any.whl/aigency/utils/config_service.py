"""Configuration service for loading and parsing agent configurations.

This module provides comprehensive configuration management for Aigency agents,
including YAML file loading, environment-specific configuration merging, and
validation through Pydantic models. It supports hierarchical configuration
structures and environment-based overrides.

The ConfigService class handles the complete configuration lifecycle from file
loading through parsing and validation, ensuring that agent configurations
are properly structured and ready for use by the agent system.

Example:
    Loading and parsing agent configuration:

    >>> service = ConfigService("config.yaml", environment="production")
    >>> config = service.config
    >>> agent_name = config.metadata.name

Attributes:
    logger: Module-level logger instance for configuration events.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from aigency.schemas.aigency_config import AigencyConfig
from aigency.utils.logger import get_logger


logger = get_logger()


class ConfigService:
    """Service for loading and managing agent configurations.

    This service handles loading YAML configuration files, merging environment-specific
    configurations, and parsing them into AigencyConfig objects.

    Attributes:
        config_file (str): Path to the main configuration file.
        environment (str | None): Environment name for environment-specific configs.
        config (AigencyConfig): Parsed configuration object.
    """

    def __init__(self, config_file: str, environment: Optional[str] = None):
        """Initialize the configuration service.

        Args:
            config_file (str): Path to the main configuration file.
            environment (str, optional): Environment name for environment-specific
                configs. Defaults to None.
        """
        self.config_file = config_file
        self.environment = environment or os.getenv("ENVIRONMENT", None)
        self.config = self._load_and_parse()

    def _load_and_parse(self) -> AigencyConfig:
        """Load YAMLs, merge them and parse according to AigencyConfig.

        Loads the main configuration file and optionally merges it with
        environment-specific configuration if available.

        Returns:
            AigencyConfig: Parsed and validated configuration object.
        """

        logger.info(f"Loading configuration from {self.config_file}")
        config = self._load_yaml(self.config_file)

        if self.environment is not None:
            logger.info(
                f"Environment '{self.environment}' detected, loading environment-specific configuration"
            )
            env_config = self._load_env_config()
            if env_config:
                logger.info(
                    f"Successfully loaded environment configuration with {len(env_config)} keys: {list(env_config.keys())}"
                )
                config = self._merge_configs(config, env_config)
                logger.debug(
                    f"Configuration merged successfully for environment '{self.environment}'"
                )
            else:
                logger.warning(
                    f"No environment-specific configuration found for '{self.environment}', using base configuration only"
                )

        return AigencyConfig(**config)

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load a YAML file.

        Args:
            file_path (str): Path to the YAML file to load.

        Returns:
            Dict[str, Any]: Parsed YAML content as dictionary.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            ValueError: If there's an error parsing the YAML file.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML {file_path}: {e}")

    def _load_env_config(self) -> Optional[Dict[str, Any]]:
        """Load environment-specific configuration.

        Attempts to load a configuration file with environment-specific naming
        pattern (e.g., config.dev.yaml for 'dev' environment).

        Returns:
            Dict[str, Any] | None: Environment configuration dictionary or None
                if no environment-specific file exists.
        """
        config_path = Path(self.config_file)
        env_file = (
            config_path.parent
            / f"{config_path.stem}.{self.environment}{config_path.suffix}"
        )

        return self._load_yaml(str(env_file)) if env_file.exists() else None

    def _merge_configs(
        self, base: Dict[str, Any], env: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge base configuration with environment configuration.

        Recursively merges environment-specific configuration into the base
        configuration, with environment values taking precedence.

        Args:
            base (Dict[str, Any]): Base configuration dictionary.
            env (Dict[str, Any] | None): Environment-specific configuration
                dictionary.

        Returns:
            Dict[str, Any]: Merged configuration dictionary.
        """
        if not env:
            return base

        result = base.copy()
        for key, value in env.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
