"""Utility functions for type conversions and environment variable handling.

This module provides essential utility functions for the Aigency framework, including
type conversions between A2A and Google GenAI formats, environment variable expansion,
URL generation, and safe asynchronous execution helpers.

The utilities handle common operations needed across the framework, such as converting
message parts between different protocol formats, managing environment variables in
configurations, and safely running coroutines in various asyncio contexts.

Example:
    Converting between A2A and GenAI formats:

    >>> a2a_part = TextPart(text="Hello world")
    >>> genai_part = convert_a2a_part_to_genai(a2a_part)
    >>> back_to_a2a = convert_genai_part_to_a2a(genai_part)

Attributes:
    logger: Module-level logger instance for utility operations.
"""

import asyncio
import os
import threading

from a2a.types import FilePart, FileWithBytes, Part, TextPart, FileWithUri
from google.genai import types

from aigency.utils.logger import get_logger

logger = get_logger()


def convert_a2a_part_to_genai(part: Part) -> types.Part:
    """Convert a single A2A Part type into a Google Gen AI Part type.

    Args:
        part (Part): The A2A Part to convert.

    Returns:
        types.Part: The equivalent Google Gen AI Part.

    Raises:
        ValueError: If the part type is not supported.
    """
    part = part.root
    if isinstance(part, TextPart):
        return types.Part(text=part.text)
    if isinstance(part, FilePart):
        if isinstance(part.file, FileWithUri):
            return types.Part(
                file_data=types.FileData(
                    file_uri=part.file.uri, mime_type=part.file.mime_type
                )
            )
        if isinstance(part.file, FileWithBytes):
            return types.Part(
                inline_data=types.Blob(
                    data=part.file.bytes, mime_type=part.file.mime_type
                )
            )
        raise ValueError(f'Unsupported file type: {type(part.file)}')

    raise ValueError(f"Unsupported part type: {type(part)}")


def convert_genai_part_to_a2a(part: types.Part) -> Part:
    """Convert a single Google Gen AI Part type into an A2A Part type.

    Args:
        part (types.Part): The Google Gen AI Part to convert.

    Returns:
        Part: The equivalent A2A Part.

    Raises:
        ValueError: If the part type is not supported.
    """
    if part.text:
        return TextPart(text=part.text)

    if part.file_data:
        return FilePart(
            file=FileWithUri(
                uri=part.file_data.file_uri,
                mime_type=part.file_data.mime_type,
            )
        )

    if part.inline_data:
        return Part(
            root=FilePart(
                file=FileWithBytes(
                    bytes=part.inline_data.data,
                    mime_type=part.inline_data.mime_type,
                )
            )
        )
    raise ValueError(f"Unsupported part type: {part}")


def expand_env_vars(env_dict):
    """Expand dictionary values using environment variables.

    Expands values in the dictionary using environment variables only if the value
    is an existing environment variable key. If the variable doesn't exist in the
    environment, leaves the literal value.

    Args:
        env_dict (dict): Dictionary with potential environment variable references.

    Returns:
        dict: Dictionary with expanded environment variable values.
    """
    result = {}
    for k, v in env_dict.items():
        if isinstance(v, str) and v in os.environ:
            result[k] = os.getenv(v)
        else:
            logger.warning(f"Environment variable {v} not found")
    return result


def generate_url(host: str, port: int, path: str = "") -> str:
    """Generate a URL from host, port, and path components.

    Args:
        host (str): Hostname or IP address.
        port (int): Port number.
        path (str, optional): URL path. Defaults to "".

    Returns:
        str: Complete URL in the format http://host:port/path.
    """
    return f"http://{host}:{port}{path}"


def safe_async_run(coro):
    """Simple wrapper to safely run async code.

    This function handles different asyncio event loop scenarios to safely
    execute coroutines, including cases where a loop is already running.

    Args:
        coro: The coroutine to execute.

    Returns:
        Any: The result of the coroutine execution.

    Raises:
        Exception: Any exception raised by the coroutine.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():

            result = None
            exception = None

            def run_in_thread():
                nonlocal result, exception
                try:
                    result = asyncio.run(coro)
                except Exception as e:
                    exception = e

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()

            if exception:
                raise exception
            return result
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)
