"""Singleton logger implementation for consistent application-wide logging.

This module provides a centralized logging system using the Singleton pattern to
ensure consistent logging behavior across the entire Aigency application. It supports
configurable log levels, multiple output handlers, and dynamic configuration updates.

The Logger class extends the Singleton base class to guarantee only one logger
instance exists throughout the application lifecycle, preventing configuration
conflicts and ensuring unified log formatting and output destinations.

Example:
    Basic logger usage:

    >>> logger = get_logger({"log_level": "DEBUG", "log_file": "app.log"})
    >>> logger.info("Application started")
    >>> logger.error("An error occurred", exc_info=True)

Attributes:
    None: This module contains only class definitions and utility functions.
"""

import logging
import sys
from typing import Optional, Dict, Any
from aigency.utils.singleton import Singleton


class Logger(Singleton):
    """Singleton logger class for consistent logging across the application.

    This class provides a centralized logging mechanism that ensures only one
    logger instance exists throughout the application lifecycle.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary for logger settings.
        _logger (logging.Logger): Internal logger instance.
        _initialized (bool): Flag to track initialization state.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the logger with optional configuration.

        Args:
            config (Dict[str, Any], optional): Dictionary containing logger
                configuration. Defaults to None.
        """
        if hasattr(self, "_initialized"):
            # If already initialized and new config is passed, update
            if config and config != getattr(self, "config", {}):
                self.config.update(config)
                self._setup_logger()
            return

        self._initialized = True
        self.config = config or {}
        self._logger = None
        self._setup_logger()

    def _setup_logger(self):
        """Configure the logger with the provided configuration.

        Sets up the internal logger instance with handlers, formatters, and
        log levels based on the configuration dictionary.
        """
        # Get logger configuration
        log_level = self.config.get("log_level", "INFO").upper()
        log_format = self.config.get(
            "log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_file = self.config.get("log_file")
        logger_name = self.config.get("logger_name", "aigency")

        # Create logger
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Avoid duplicating handlers if they already exist
        if self._logger.handlers:
            return

        # Create formatter
        formatter = logging.Formatter(log_format)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

    def debug(self, message: str, *args, **kwargs):
        """Log a debug message.

        Args:
            message (str): The message to log.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log an info message.

        Args:
            message (str): The message to log.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log a warning message.

        Args:
            message (str): The message to log.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log an error message.

        Args:
            message (str): The message to log.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log a critical message.

        Args:
            message (str): The message to log.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log an exception with traceback.

        Args:
            message (str): The message to log.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._logger.exception(message, *args, **kwargs)

    def set_level(self, level: str):
        """Change the logging level dynamically.

        Args:
            level (str): The new logging level as a string.
        """
        log_level = level.upper()
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))
        for handler in self._logger.handlers:
            handler.setLevel(getattr(logging, log_level, logging.INFO))

    def get_logger(self):
        """Get the internal logger instance.

        Returns:
            logging.Logger: The internal logging.Logger instance.
        """
        return self._logger


# Convenience function to get the logger instance
def get_logger(config: Optional[Dict[str, Any]] = None) -> Logger:
    """Get the singleton logger instance.

    If this is the first call and config is provided, that configuration is used.

    Args:
        config (Dict[str, Any], optional): Optional configuration for the logger
            (only used on first call). Defaults to None.

    Returns:
        Logger: Singleton Logger instance.
    """
    return Logger(config)
