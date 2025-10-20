import importlib
import os
import pkgutil
from mcp.server.fastmcp import FastMCP


def load_tools():
    """Load tools based on lite mode configuration."""
    import src.tools as tools_pkg

    # Check if lite mode is enabled
    lite_mode = os.getenv("LITE_MODE", "false").lower() == "true"

    if lite_mode:
        # In lite mode, only load the redis_execute tool
        importlib.import_module("src.tools.redis_execute")
    else:
        # In normal mode, load all tools except redis_execute
        for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
            if module_name != "redis_execute":
                importlib.import_module(f"src.tools.{module_name}")


def load_all_tools():
    """Load all tools (for testing or fallback)."""
    import src.tools as tools_pkg

    for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
        importlib.import_module(f"src.tools.{module_name}")


# Initialize FastMCP server
mcp = FastMCP("Redis MCP Server", dependencies=["redis", "dotenv", "numpy"])

# Load tools based on lite mode configuration
load_tools()
