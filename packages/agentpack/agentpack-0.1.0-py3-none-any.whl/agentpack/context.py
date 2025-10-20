"""Execution context implementation."""

import os
from typing import Any, Optional

import httpx
import structlog
from opentelemetry import trace
from opentelemetry.trace import Span as OtelSpan

from agentpack.errors import HttpError, SecretNotFoundError
from agentpack.types import (
    ExecutionContext,
    HttpClient,
    HttpResponse,
    Logger,
    RequestMetadata,
    SecretManager,
    Span,
    Tracer,
)


class EnvSecretManager:
    """Environment variable-based secret manager (MVP)."""

    async def get(self, key: str) -> Optional[str]:
        """Get a secret from environment variables."""
        return os.environ.get(key)

    async def require(self, key: str) -> str:
        """Get a required secret (raises if not found)."""
        value = await self.get(key)
        if value is None:
            raise SecretNotFoundError(key)
        return value

    async def get_many(self, keys: list[str]) -> dict[str, str]:
        """Get multiple secrets."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result


class HttpxClient:
    """httpx-based HTTP client with retries."""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3) -> None:
        self.client = httpx.AsyncClient(timeout=timeout)
        self.max_retries = max_retries

    async def get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HttpResponse:
        """Make a GET request."""
        try:
            response = await self.client.get(
                url, params=params, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            return HttpResponse(
                data=response.json() if response.headers.get("content-type", "").startswith(
                    "application/json"
                ) else response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.HTTPStatusError as e:
            raise HttpError(
                f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                e.response.status_code,
                e.response.text,
            )
        except httpx.RequestError as e:
            raise HttpError(f"Request failed: {e}", 0)

    async def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HttpResponse:
        """Make a POST request."""
        try:
            response = await self.client.post(
                url, data=data, json=json, params=params, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            return HttpResponse(
                data=response.json() if response.headers.get("content-type", "").startswith(
                    "application/json"
                ) else response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.HTTPStatusError as e:
            raise HttpError(
                f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                e.response.status_code,
                e.response.text,
            )
        except httpx.RequestError as e:
            raise HttpError(f"Request failed: {e}", 0)

    async def put(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HttpResponse:
        """Make a PUT request."""
        try:
            response = await self.client.put(
                url, data=data, json=json, params=params, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            return HttpResponse(
                data=response.json() if response.headers.get("content-type", "").startswith(
                    "application/json"
                ) else response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.HTTPStatusError as e:
            raise HttpError(
                f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                e.response.status_code,
                e.response.text,
            )
        except httpx.RequestError as e:
            raise HttpError(f"Request failed: {e}", 0)

    async def delete(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HttpResponse:
        """Make a DELETE request."""
        try:
            response = await self.client.delete(
                url, params=params, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            return HttpResponse(
                data=response.json() if response.headers.get("content-type", "").startswith(
                    "application/json"
                ) else response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.HTTPStatusError as e:
            raise HttpError(
                f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                e.response.status_code,
                e.response.text,
            )
        except httpx.RequestError as e:
            raise HttpError(f"Request failed: {e}", 0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


class StructlogLogger:
    """structlog-based structured logger."""

    def __init__(self) -> None:
        self.logger = structlog.get_logger()

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self.logger.info(message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self.logger.error(message, **kwargs)


class OtelSpanWrapper:
    """Wrapper for OpenTelemetry span."""

    def __init__(self, span: OtelSpan) -> None:
        self._span = span

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        self._span.set_attribute(key, value)

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        """Set multiple attributes."""
        self._span.set_attributes(attributes)

    def record_exception(self, exception: Exception) -> None:
        """Record an exception."""
        self._span.record_exception(exception)

    def end(self) -> None:
        """End the span."""
        self._span.end()


class OtelTracer:
    """OpenTelemetry tracer wrapper."""

    def __init__(self, service_name: str) -> None:
        self.tracer = trace.get_tracer(service_name)

    def start_span(self, name: str, attributes: Optional[dict[str, Any]] = None) -> Span:
        """Start a new span."""
        span = self.tracer.start_span(name, attributes=attributes)
        return OtelSpanWrapper(span)  # type: ignore

    def get_current_span(self) -> Optional[Span]:
        """Get the current span."""
        span = trace.get_current_span()
        if span:
            return OtelSpanWrapper(span)  # type: ignore
        return None


def create_execution_context(metadata: RequestMetadata) -> ExecutionContext:
    """Create an execution context."""
    return ExecutionContext(
        secrets=EnvSecretManager(),  # type: ignore
        http=HttpxClient(),  # type: ignore
        logger=StructlogLogger(),  # type: ignore
        tracer=OtelTracer("agentpack-tool"),  # type: ignore
        metadata=metadata,
    )
