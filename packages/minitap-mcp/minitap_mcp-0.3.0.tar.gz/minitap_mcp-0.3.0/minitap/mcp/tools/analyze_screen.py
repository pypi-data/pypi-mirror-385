from pathlib import Path
from jinja2 import Template
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from uuid import uuid4

from pydantic import Field

from minitap.mcp.core.config import settings
from minitap.mcp.core.decorators import handle_tool_errors
from minitap.mcp.core.device import capture_screenshot, find_mobile_device
from minitap.mcp.core.llm import get_minitap_llm
from minitap.mcp.core.utils import compress_base64_jpeg, get_screenshot_message_for_llm
from minitap.mcp.main import mcp


@mcp.tool(
    name="analyze_screen",
    description="""
    Analyze what is shown on the mobile device screen.
    This tool takes a screenshot file path and uses a vision-capable LLM
    to analyze and describe what's on the screen. Useful for understanding
    UI elements, extracting text, or identifying specific features.
    """,
)
@handle_tool_errors
async def analyze_screen(
    prompt: str = Field(
        description="Prompt for the analysis.",
    ),
    device_id: str | None = Field(
        default=None,
        description="ID of the device screen to analyze. "
        "If not provided, the first available device is taken.",
    ),
) -> str | list | dict:
    system_message = Template(
        Path(__file__).parent.joinpath("screen_analyzer.md").read_text(encoding="utf-8")
    ).render()

    # Find the device and capture screenshot
    device = find_mobile_device(device_id=device_id)
    screenshot_base64 = capture_screenshot(device)
    compressed_image_base64 = compress_base64_jpeg(screenshot_base64)

    messages: list[BaseMessage] = [
        SystemMessage(content=system_message),
        get_screenshot_message_for_llm(compressed_image_base64),
        HumanMessage(content=prompt),
    ]

    llm = get_minitap_llm(
        trace_id=str(uuid4()),
        remote_tracing=True,
        model=settings.VISION_MODEL,
        temperature=1,
    )
    response = await llm.ainvoke(messages)
    return response.content
