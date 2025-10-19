"""Tool configuration schemas for agent capabilities.

This module defines comprehensive Pydantic models for configuring various types
of tools that agents can use within the Aigency framework. It supports multiple
tool types including MCP (Model Context Protocol) tools and function-based tools,
with specific configuration schemas for each type.

The module provides a flexible and extensible tool configuration system that
allows agents to integrate with different tool providers and execution environments,
enabling rich agent capabilities through external tool integration.

Example:
    Configuring different tool types:

    >>> function_tool = FunctionTool(
    ...     type=ToolType.FUNCTION,
    ...     name="calculator",
    ...     module_path="math_tools",
    ...     function_name="add"
    ... )
    >>> mcp_tool = McpTool(
    ...     type=ToolType.MCP,
    ...     name="file_manager",
    ...     mcp_config=McpTypeStdio(command="file-server")
    ... )

Attributes:
    None: This module contains only Pydantic model definitions and enums.
"""

from enum import Enum
from typing import Dict, List, Optional, TypeAlias

from pydantic import BaseModel


class ToolType(str, Enum):
    """Enum for tool types.

    Defines the available types of tools that can be used by agents.

    Attributes:
        MCP: MCP (Model Context Protocol) based tools.
        FUNCTION: Function-based tools loaded from Python modules.
    """

    MCP = "mcp"
    FUNCTION = "function"


class BaseTool(BaseModel):
    """Define an external tool that the agent can use.

    Base class for all tool configurations containing common attributes.

    Attributes:
        type (ToolType): The type of tool (MCP or FUNCTION).
        name (str): Name identifier for the tool.
        description (str): Human-readable description of what the tool does.
    """

    type: ToolType
    name: str
    description: str


class FunctionTool(BaseTool):
    """Configuration for function-based tools.

    Tools that are loaded from Python functions in specified modules.

    Attributes:
        module_path (str): Python module path containing the function.
        function_name (str): Name of the function to load from the module.
    """

    module_path: str
    function_name: str


class McpTypeStreamable(BaseModel):
    """Model for streamable tool type.

    Configuration for MCP tools that communicate via HTTP streaming.

    Attributes:
        url (str): Base URL for the MCP server.
        port (int): Port number for the MCP server.
        path (str): URL path for the MCP endpoint. Defaults to "/".
    """

    url: str
    port: int
    path: str = "/"


class McpTypeStdio(BaseModel):
    """Model for stdio tool type.

    Configuration for MCP tools that communicate via standard input/output.

    Attributes:
        command (str): Command to execute for the MCP server.
        args (List[str]): Command line arguments for the MCP server.
        env (Dict[str, str], optional): Environment variables for the MCP server.
    """

    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


class McpTool(BaseTool):
    """Configuration for MCP-based tools.

    Tools that use the Model Context Protocol for communication.

    Attributes:
        mcp_config (McpTypeStreamable | McpTypeStdio): Configuration for the MCP
            connection, either streamable HTTP or stdio based.
    """

    mcp_config: McpTypeStreamable | McpTypeStdio


Tool: TypeAlias = FunctionTool | McpTool
