"""
Agentpack Python SDK

Python SDK for building Agentpack tools with type safety and observability.

This is a THIN SDK - users only interact with the @tool decorator.
All server/runtime logic has been moved to a separate runtime package.
"""

from agentpack.errors import (
    HttpError,
    InternalError,
    SecretNotFoundError,
    TimeoutError,
    ToolError,
    ValidationError,
)
from agentpack.tool import tool
from agentpack.types import ExecutionContext, Tool

__version__ = "0.1.0"

__all__ = [
    # Main API - ONLY tool decorator
    "tool",
    # Types
    "Tool",
    "ExecutionContext",
    # Errors
    "ToolError",
    "ValidationError",
    "SecretNotFoundError",
    "HttpError",
    "TimeoutError",
    "InternalError",
]
