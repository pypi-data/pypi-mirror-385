import requests

from minitap.mcp.core.decorators import handle_tool_errors
from minitap.mcp.main import mcp


@mcp.tool(
    name="go_back",
    tags={"requires-maestro"},
    description="""
    Sends a 'back' command to the mobile device automation server.
    """,
)
@handle_tool_errors
async def go_back() -> str:
    """Send a back command to the mobile device."""
    try:
        response = requests.post(
            "http://localhost:9999/api/run-command",
            headers={
                "User-Agent": "python-requests/2.32.4",
                "Accept-Encoding": "gzip, deflate, zstd",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
            },
            json={"yaml": "back\n"},
            timeout=30,
        )

        if response.status_code == 200:
            return f"Successfully sent back command. Response: {response.text}"
        else:
            return (
                f"Failed to send back command. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )

    except requests.exceptions.RequestException as e:
        return f"Error sending back command: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
