import logging

from openmarkets.core.config import Settings
from openmarkets.core.fastmcp import FastMCP
from openmarkets.core.registry import ToolRegistry

logger = logging.getLogger(__name__)


def create_server(config: Settings) -> FastMCP:
    """Creates and configures the MCP server instance.

    Initializes the MCP server and registers all available tools using ToolRegistry.
    Logs and re-raises exceptions during registration.

    Args:
        config (Settings): Configuration object containing tool module reference.

    Returns:
        FastMCP: Configured MCP server instance.

    Raises:
        Exception: If tool registration fails.
    """
    mcp: FastMCP = FastMCP(
        name="Open Markets Server",
        instructions="This server allows for the integration of various market data tools.",
    )
    try:
        registry: ToolRegistry = ToolRegistry()
        registry.register_tools_from_module(mcp, config.tools_module)
        logger.info("Tool registration process completed.")
    except Exception as exc:
        logger.exception("Failed to initialize ToolRegistry or register tools.")
        raise exc

    return mcp
