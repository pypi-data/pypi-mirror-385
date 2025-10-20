"""Type definitions for Agentpack SDK."""

from typing import Any, Awaitable, Callable, Optional, Protocol, TypeVar

from pydantic import BaseModel

# Type variables
TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class RequestMetadata(BaseModel):
    """Request metadata."""

    request_id: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class SecretManager(Protocol):
    """Secret manager interface."""

    async def get(self, key: str) -> Optional[str]:
        """Get a secret by key (returns None if not found)."""
        ...

    async def require(self, key: str) -> str:
        """Get a required secret (raises SecretNotFoundError if not found)."""
        ...

    async def get_many(self, keys: list[str]) -> dict[str, str]:
        """Get multiple secrets."""
        ...


class HttpClient(Protocol):
    """HTTP client interface."""

    async def get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> "HttpResponse":
        """Make a GET request."""
        ...

    async def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> "HttpResponse":
        """Make a POST request."""
        ...

    async def put(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> "HttpResponse":
        """Make a PUT request."""
        ...

    async def delete(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> "HttpResponse":
        """Make a DELETE request."""
        ...


class HttpResponse(BaseModel):
    """HTTP response wrapper."""

    data: Any
    status_code: int
    headers: dict[str, str]


class Logger(Protocol):
    """Logger interface."""

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    def warn(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        ...


class Span(Protocol):
    """OpenTelemetry span interface."""

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        ...

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        """Set multiple attributes."""
        ...

    def record_exception(self, exception: Exception) -> None:
        """Record an exception."""
        ...

    def end(self) -> None:
        """End the span."""
        ...


class Tracer(Protocol):
    """OpenTelemetry tracer interface."""

    def start_span(self, name: str, attributes: Optional[dict[str, Any]] = None) -> Span:
        """Start a new span."""
        ...

    def get_current_span(self) -> Optional[Span]:
        """Get the current span."""
        ...


class ExecutionContext:
    """Execution context provided to tool handlers."""

    def __init__(
        self,
        secrets: SecretManager,
        http: HttpClient,
        logger: Logger,
        tracer: Tracer,
        metadata: RequestMetadata,
    ) -> None:
        self.secrets = secrets
        self.http = http
        self.logger = logger
        self.trace = tracer
        self.metadata = metadata


# Tool handler type
ToolHandler = Callable[[TInput, ExecutionContext], Awaitable[TOutput]]


class Tool:
    """Tool instance."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: type[BaseModel],
        output_schema: type[BaseModel],
        handler: Callable[[Any, ExecutionContext], Awaitable[Any]],
    ) -> None:
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self._handler = handler

    async def execute(self, input_data: Any, ctx: ExecutionContext) -> Any:
        """Execute the tool."""
        # Validate input
        validated_input = self.input_schema.model_validate(input_data)

        # Execute handler
        output = await self._handler(validated_input, ctx)

        # Validate output
        validated_output = self.output_schema.model_validate(output)

        return validated_output

    def to_dict(self) -> dict[str, Any]:
        """Convert tool to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.model_json_schema(),
            "output_schema": self.output_schema.model_json_schema(),
        }


class ServerOptions(BaseModel):
    """Server configuration options."""

    port: int = 8080
    host: str = "0.0.0.0"
    service_name: str = "agentpack-tool"
    otlp_endpoint: Optional[str] = None
