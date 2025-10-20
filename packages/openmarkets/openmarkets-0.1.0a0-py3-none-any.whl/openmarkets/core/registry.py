import importlib
import inspect
import logging
import pkgutil
from types import ModuleType
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Singleton registry for discovering and registering tool functions with an MCP server.

    This class provides methods to dynamically discover and register tool functions
    from a specified package with an MCP server instance.
    """

    _instance: Optional["ToolRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

    def register_tools_from_module(self, mcp: Any, module_name: str = "openmarkets.tools") -> None:
        """
        Dynamically discovers and registers all public tool functions from the specified package.

        Args:
            mcp (Any): The MCP server instance to register tools with.
            tools_module_name (str): The package name containing tool modules.

        Returns:
            None
        """
        try:
            tools_module = importlib.import_module(module_name)
        except ImportError:
            logger.error(f"Could not import tools package: {module_name}")
            return

        if not hasattr(tools_module, "__path__"):
            logger.error(f"Tools package {module_name} does not have __path__, cannot discover modules.")
            return

        package_path = tools_module.__path__

        for _, module_name, _ in pkgutil.walk_packages(package_path, prefix=tools_module.__name__ + "."):
            if module_name.endswith(".__init__"):
                continue
            try:
                module = importlib.import_module(module_name)
                # Always call register_module_functions for test compatibility
                self.register_module_functions(mcp, module)
                logger.info(f"Successfully registered tools from {module_name}")
            except ImportError as e:
                logger.error(f"Failed to import module {module_name}: {e}")
            except Exception as e:
                logger.error(f"Error registering tools from {module_name}: {e}")

    def register_module_functions(self, mcp: Any, module: ModuleType) -> None:
        """
        Register all public functions in a module as tools with the MCP server.

        Args:
            mcp (Any): The MCP server instance.
            module (ModuleType): The module containing tool functions.

        Returns:
            None
        """
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_") or name.startswith("register_"):
                continue
            try:
                mcp.tool()(func)
                logger.debug(f"Registered tool: {name} from module: {getattr(module, '__name__', repr(module))}")
            except Exception as e:
                logger.error(
                    f"Error registering function '{name}' from module '{getattr(module, '__name__', repr(module))}': {e}"
                )
                raise e
