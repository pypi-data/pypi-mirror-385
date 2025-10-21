"""Decorators for MCP tools."""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from minitap.mcp.core.device import DeviceNotFoundError

F = TypeVar("F", bound=Callable[..., Any])


def handle_tool_errors[T: Callable[..., Any]](func: T) -> T:
    """
    Decorator that catches all exceptions in MCP tools and returns error messages.

    This prevents unhandled exceptions from causing infinite loops in the MCP server.
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except DeviceNotFoundError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error in {func.__name__}: {type(e).__name__}: {str(e)}"

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except DeviceNotFoundError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error in {func.__name__}: {type(e).__name__}: {str(e)}"

    # Check if the function is async
    if inspect.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    else:
        return sync_wrapper  # type: ignore
