"""Device health monitoring poller for the MCP server."""

import logging
import time
import threading

from minitap.mcp.core.device import list_available_devices
from minitap.mobile_use.sdk import Agent

logger = logging.getLogger(__name__)


def device_health_poller(stop_event: threading.Event, agent: Agent) -> None:
    """
    Background poller that monitors device availability and agent health.
    Runs every 5 seconds to ensure a device is connected and the agent is healthy.

    Args:
        agent: The Agent instance to monitor and reinitialize if needed.
    """
    while not stop_event.is_set():
        try:
            time.sleep(5)

            devices = list_available_devices()

            if len(devices) > 0:
                if not agent.is_healthy():
                    logger.warning("Agent is not healthy. Reinitializing...")
                    agent.clean(force=True)
                    agent.init()
                    logger.info("Agent reinitialized successfully")
            else:
                logger.info("No mobile device found, retrying in 5 seconds...")

        except Exception as e:
            logger.error(f"Error in device health poller: {e}")
    agent.clean(force=True)
