"""Tool factory for dynamically loading and managing agent tools.

This module provides a flexible way to load different types of tools based on
configuration using the Strategy pattern and Pydantic for validation. It supports
both MCP (Model Context Protocol) tools and function-based tools, handling their
instantiation and configuration automatically.

The ToolGenerator class uses a strategy-based approach to delegate tool creation
to specialized loading functions based on the tool type, providing a clean and
extensible architecture for tool management.

Example:
    Creating tools from configuration:

    >>> tool_config = FunctionTool(type=ToolType.FUNCTION, name="calculator",
    ...                           module_path="math_tools", function_name="add")
    >>> tool = ToolGenerator.create_tool(tool_config)
    >>> result = tool(2, 3)

Attributes:
    None: This module contains only class definitions and strategy mappings.
"""

import importlib
from typing import Any, Optional

from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
    StreamableHTTPConnectionParams,
)

from aigency.schemas.agent.tools import (
    FunctionTool,
    McpTool,
    McpTypeStdio,
    McpTypeStreamable,
    Tool,
    ToolType,
)
from aigency.utils.utils import expand_env_vars


class ToolGenerator:
    """Generator for creating tools based on configuration.

    This class provides static methods to dynamically load and create different
    types of tools (MCP and Function tools) based on their configuration using
    the Strategy pattern.

    Attributes:
        STRATEGIES (dict): Dictionary mapping tool types to their loading functions.
    """

    @staticmethod
    def load_function_tool(config: FunctionTool) -> Any:
        """Load a function tool from configuration.

        Dynamically imports a Python module and retrieves the specified function
        to use as a tool.

        Args:
            config (FunctionTool): Configuration containing module path and function name.

        Returns:
            Any: The loaded function object.

        Raises:
            ValueError: If the module cannot be imported or function not found.
        """
        try:
            module = importlib.import_module(config.module_path)
            return getattr(module, config.function_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Error loading function tool: {e}")

    @staticmethod
    def load_mcp_tool(config: McpTool) -> Any:
        """Load an MCP tool from configuration.

        Creates an MCP toolset based on the connection type (streamable HTTP or stdio).

        Args:
            config (McpTool): Configuration containing MCP connection details.

        Returns:
            Any: The created MCPToolset instance.
        """

        if isinstance(config.mcp_config, McpTypeStreamable):
            url = f"http://{config.mcp_config.url}:{config.mcp_config.port}{config.mcp_config.path}"
            return MCPToolset(connection_params=StreamableHTTPConnectionParams(url=url))
        elif isinstance(config.mcp_config, McpTypeStdio):
            command = config.mcp_config.command
            args = config.mcp_config.args
            env = expand_env_vars(config.mcp_config.env)

            return MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=command, args=args, env=env
                    )
                )
            )

    STRATEGIES = {
        ToolType.MCP: load_mcp_tool,
        ToolType.FUNCTION: load_function_tool,
    }

    @staticmethod
    def create_tool(tool: Tool) -> Optional[Any]:
        """Create a tool based on its configuration.

        Uses the Strategy pattern to delegate tool creation to the appropriate
        loading function based on the tool type.

        Args:
            tool (Tool): Tool configuration (FunctionTool or McpTool).

        Returns:
            Any | None: The created tool instance or None if creation failed.

        Raises:
            ValueError: If tool type is not supported or config is invalid.
            KeyError: If tool type is not found in STRATEGIES.
        """

        return ToolGenerator.STRATEGIES[tool.type](tool)
