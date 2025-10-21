"""MCP server for mobile-use with screen analysis capabilities."""

import argparse
import logging
import os
import sys
import threading

# Fix Windows console encoding for Unicode characters (emojis in logs)
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    os.environ["PYTHONIOENCODING"] = "utf-8"

    try:
        import colorama

        colorama.init(strip=False, convert=True, wrap=True)
    except ImportError:
        pass


from fastmcp import FastMCP  # noqa: E402

from minitap.mcp.core.config import settings  # noqa: E402
from minitap.mobile_use.config import settings as sdk_settings
from minitap.mcp.core.device import (
    DeviceInfo,  # noqa: E402
    list_available_devices,
)
from minitap.mcp.server.middleware import MaestroCheckerMiddleware
from minitap.mcp.server.poller import device_health_poller


def main() -> None:
    """Main entry point for the MCP server."""

    parser = argparse.ArgumentParser(description="Mobile Use MCP Server")
    parser.add_argument("--api-key", type=str, required=False, default=None)
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run as network server (uses MCP_SERVER_HOST and MCP_SERVER_PORT from env)",
    )

    args = parser.parse_args()
    print("parsing args")
    print(args)

    if args.api_key:
        os.environ["MINITAP_API_KEY"] = args.api_key
        settings.__init__()
        sdk_settings.__init__()

    if not settings.MINITAP_API_KEY:
        raise ValueError("Minitap API key is required to run the MCP")

    # Run MCP server with optional host/port for remote access
    if args.server:
        logger.info(f"Starting MCP server on {settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
        mcp_lifespan(
            transport="http",
            host=settings.MCP_SERVER_HOST,
            port=settings.MCP_SERVER_PORT,
        )
    else:
        logger.info("Starting MCP server in local mode")
        mcp_lifespan()


logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="mobile-use-mcp",
    instructions="""
        This server provides analysis tools for connected
        mobile devices (iOS or Android).
        Call get_available_devices() to list them.
    """,
)

from minitap.mcp.tools import (  # noqa: E402, F401
    analyze_screen,  # noqa: E402, F401
    execute_mobile_command,  # noqa: E402, F401
)


@mcp.resource("data://devices")
def get_available_devices() -> list[DeviceInfo]:
    """Provides a list of connected mobile devices (iOS or Android)."""
    return list_available_devices()


def mcp_lifespan(**mcp_run_kwargs):
    from minitap.mcp.core.agents import get_mobile_use_agent  # noqa: E402

    agent = get_mobile_use_agent()
    mcp.add_middleware(MaestroCheckerMiddleware(agent))

    # Start device health poller in background
    logger.info("Device health poller started")
    stop_event = threading.Event()
    poller_thread = threading.Thread(
        target=device_health_poller,
        args=(
            stop_event,
            agent,
        ),
    )
    poller_thread.start()

    try:
        mcp.run(**mcp_run_kwargs)
    except KeyboardInterrupt:
        pass

    # Stop device health poller
    stop_event.set()
    logger.info("Device health poller stopping...")
    poller_thread.join()
    logger.info("Device health poller stopped")
