"""Error classes for Agentpack SDK."""

from typing import Any, Optional


class ToolError(Exception):
    """Base error class for all tool errors."""

    def __init__(self, message: str, code: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": str(self),
            "details": self.details,
        }


class ValidationError(ToolError):
    """Validation error (input/output schema validation failed)."""

    def __init__(self, message: str, errors: list[Any]) -> None:
        super().__init__(message, "VALIDATION_ERROR", errors)


class SecretNotFoundError(ToolError):
    """Secret not found error."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Secret not found: {key}", "SECRET_NOT_FOUND", {"key": key})


class HttpError(ToolError):
    """HTTP error (external API call failed)."""

    def __init__(self, message: str, status_code: int, response: Optional[Any] = None) -> None:
        super().__init__(
            message, "HTTP_ERROR", {"status_code": status_code, "response": response}
        )
        self.status_code = status_code
        self.response = response


class TimeoutError(ToolError):
    """Timeout error."""

    def __init__(self, message: str, timeout_ms: int) -> None:
        super().__init__(message, "TIMEOUT", {"timeout_ms": timeout_ms})


class InternalError(ToolError):
    """Internal error (unexpected error in tool execution)."""

    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        details = None
        if original_error:
            details = {
                "original_error": str(original_error),
                "type": type(original_error).__name__,
            }
        super().__init__(message, "INTERNAL_ERROR", details)
        self.original_error = original_error
