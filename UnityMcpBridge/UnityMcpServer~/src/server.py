from mcp.server.fastmcp import FastMCP, Context, Image
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any
from config import config
from logging_utils import setup_logging
from tools import register_all_tools
from unity_connection import get_unity_connection, UnityConnection
import time

# Configure logging before doing anything else so startup logs are structured
setup_logging()
logger = logging.getLogger("mcp-for-unity-server")
logger.info("Unity MCP protocol version %s", config.protocol_version)

# Import telemetry only after logging is configured to ensure its logs use stderr and proper levels
# Ensure a slightly higher telemetry timeout unless explicitly overridden by env
try:


    # Ensure generous timeout unless explicitly overridden by env
    if not os.environ.get("UNITY_MCP_TELEMETRY_TIMEOUT"):
        os.environ["UNITY_MCP_TELEMETRY_TIMEOUT"] = "5.0"
except Exception:
    pass
from telemetry import record_telemetry, record_milestone, RecordType, MilestoneType

# Global connection state
_unity_connection: UnityConnection = None


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Handle server startup and shutdown."""
    global _unity_connection
    logger.info("MCP for Unity Server starting up")
    
    # Record server startup telemetry
    start_time = time.time()
    start_clk = time.perf_counter()
    try:
        from pathlib import Path
        ver_path = Path(__file__).parent / "server_version.txt"
        server_version = ver_path.read_text(encoding="utf-8").strip()
    except Exception:
        server_version = "unknown"
    # Defer initial telemetry by 1s to avoid stdio handshake interference
    import threading
    def _emit_startup():
        try:
            record_telemetry(RecordType.STARTUP, {
                "server_version": server_version,
                "startup_time": start_time,
            })
            record_milestone(MilestoneType.FIRST_STARTUP)
        except Exception:
            logger.debug("Deferred startup telemetry failed", exc_info=True)
    threading.Timer(1.0, _emit_startup).start()
    
    try:
        skip_connect = os.environ.get("UNITY_MCP_SKIP_STARTUP_CONNECT", "").lower() in ("1", "true", "yes", "on")
        if skip_connect:
            logger.info("Skipping Unity connection on startup (UNITY_MCP_SKIP_STARTUP_CONNECT=1)")
        else:
            _unity_connection = get_unity_connection()
            logger.info("Connected to Unity on startup")
            
            # Record successful Unity connection (deferred)
            import threading as _t
            _t.Timer(1.0, lambda: record_telemetry(
                RecordType.UNITY_CONNECTION,
                {
                    "status": "connected",
                    "connection_time_ms": (time.perf_counter() - start_clk) * 1000,
                }
            )).start()
            
    except ConnectionError as e:
        logger.warning("Could not connect to Unity on startup: %s", e)
        _unity_connection = None
        
        # Record connection failure (deferred)
        import threading as _t
        _err_msg = str(e)[:200]
        _t.Timer(1.0, lambda: record_telemetry(
            RecordType.UNITY_CONNECTION,
            {
                "status": "failed",
                "error": _err_msg,
                "connection_time_ms": (time.perf_counter() - start_clk) * 1000,
            }
        )).start()
    except Exception as e:
        logger.warning("Unexpected error connecting to Unity on startup: %s", e)
        _unity_connection = None
        import threading as _t
        _err_msg = str(e)[:200]
        _t.Timer(1.0, lambda: record_telemetry(
            RecordType.UNITY_CONNECTION,
            {
                "status": "failed",
                "error": _err_msg,
                "connection_time_ms": (time.perf_counter() - start_clk) * 1000,
            }
        )).start()
        
    try:
        # Yield the connection object so it can be attached to the context
        # The key 'bridge' matches how tools like read_console expect to access it (ctx.bridge)
        yield {"bridge": _unity_connection}
    finally:
        if _unity_connection:
            _unity_connection.disconnect()
            _unity_connection = None
        logger.info("MCP for Unity Server shut down")

# Initialize MCP server
mcp = FastMCP(
    "mcp-for-unity-server",
    description="Unity Editor integration via Model Context Protocol",
    lifespan=server_lifespan
)

# Register all tools
register_all_tools(mcp)

# Asset Creation Strategy


@mcp.prompt()
def asset_creation_strategy() -> str:
    """Guide for discovering and using MCP for Unity tools effectively."""
    return (
        "Available MCP for Unity Server Tools:\n\n"
        "- `manage_editor`: Controls editor state and queries info.\n"
        "- `manage_menu_item`: Executes, lists and checks for the existence of Unity Editor menu items.\n"
        "- `read_console`: Reads or clears Unity console messages, with filtering options.\n"
        "- `manage_scene`: Manages scenes.\n"
        "- `manage_gameobject`: Manages GameObjects in the scene.\n"
        "- `manage_script`: Manages C# script files.\n"
        "- `manage_asset`: Manages prefabs and assets.\n"
        "- `manage_shader`: Manages shaders.\n\n"
        "Tips:\n"
        "- Create prefabs for reusable GameObjects.\n"
        "- Always include a camera and main light in your scenes.\n"
        "- Unless specified otherwise, paths are relative to the project's `Assets/` folder.\n"
        "- After creating or modifying scripts with `manage_script`, allow Unity to recompile; use `read_console` to check for compile errors.\n"
        "- Use `manage_menu_item` for interacting with Unity systems and third party tools like a user would.\n"
        "- List menu items before using them if you are unsure of the menu path.\n"
        "- If a menu item seems missing, refresh the cache: use manage_menu_item with action='list' and refresh=true, or action='refresh'. Avoid refreshing every time; prefer refresh only when the menu set likely changed.\n"
    )


def main() -> None:
    """Entry point used by the console script."""
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


# Run the server
if __name__ == "__main__":
    main()
