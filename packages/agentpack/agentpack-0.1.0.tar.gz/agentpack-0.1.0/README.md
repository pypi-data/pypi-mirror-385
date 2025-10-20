# agentpack

**Zero-Config Python SDK for Agentpack Tools**

Drop a `.py` file in your repo and get a production-ready, containerized, gRPC-enabled tool—instantly. No servers. No Docker. No infrastructure code.

## Installation

```bash
pip install agentpack
# or
poetry add agentpack
# or
uv pip install agentpack
```

## Quick Start

### 1. Write ONLY Business Logic

```python
# tools/greet.py
from pydantic import BaseModel
from agentpack import tool, ExecutionContext

class GreetInput(BaseModel):
    name: str

class GreetOutput(BaseModel):
    greeting: str

@tool(
    name="greet",
    description="Greet a person by name",
    input_schema=GreetInput,
    output_schema=GreetOutput,
)
async def greet(input: GreetInput, ctx: ExecutionContext) -> GreetOutput:
    ctx.logger.info("Greeting user", name=input.name)
    return GreetOutput(greeting=f"Hello, {input.name}!")
```

### 2. That's It!

No step 2. **Agentpack Builder** automatically:
- Discovers tools in `tools/` directory
- Generates `.agentpack-manifest.json`
- Creates optimized Dockerfile
- Builds OCI image with gRPC runtime
- Deploys to container backend

**Agentpack Runtime** automatically:
- Loads tools from manifest
- Starts gRPC server (port 50051)
- Handles execution via Rust core
- Provides full observability

## Zero-Config Architecture

```
┌─────────────────────────────────────────────────┐
│  YOU: Write tools/calculator.py                 │
│  ↓                                              │
│  BUILDER: Scan → Manifest → Dockerfile → Image │
│  ↓                                              │
│  RUNTIME: Load → gRPC Server → Execute         │
│  ↓                                              │
│  RUST CORE: Orchestrate with Tower middleware  │
└─────────────────────────────────────────────────┘
```

**You own**: Business logic (100% focus)
**Agentpack owns**: Servers, containers, orchestration, observability

## Features

### Built-In, Zero Setup:
- ✅ **Type-Safe**: Full type inference with Pydantic
- ✅ **Validated**: Automatic input/output validation
- ✅ **Observable**: OpenTelemetry tracing (no config)
- ✅ **Secure**: Secret management via dashboard
- ✅ **Resilient**: HTTP client with automatic retries
- ✅ **Structured Logging**: Request-scoped context
- ✅ **gRPC**: High-performance protocol (auto-configured)
- ✅ **Containerized**: OCI images with base runtime
- ✅ **Sandboxed**: gVisor/Firecracker isolation

## Execution Context

Every tool handler receives `ctx` with production-ready utilities:

### Secrets

```python
# Get optional secret
api_key = await ctx.secrets.get("API_KEY")

# Get required secret (raises if missing)
api_key = await ctx.secrets.require("API_KEY")

# Secrets configured via Agentpack Dashboard:
# - vault://kv/my-secret
# - aws-sm://secret-name
# - gcp-sm://projects/*/secrets/*
```

### HTTP Client

```python
# GET with automatic retries
response = await ctx.http.get(
    "https://api.example.com/data",
    params={"limit": 10},
    headers={"Authorization": f"Bearer {token}"},
)

# POST, PUT, DELETE also available
response = await ctx.http.post(
    "https://api.example.com/data",
    json={"name": "value"},
)
```

### Logger

```python
ctx.logger.info("Processing request", user_id="123")
ctx.logger.error("Something went wrong", error=str(err))

# Logs automatically include:
# - Request ID
# - Trace ID
# - Tool name
# - Timestamp
```

### Tracer (OpenTelemetry)

```python
span = ctx.trace.start_span("external-api-call")
try:
    # ... do work ...
    span.set_attribute("items.count", len(items))
finally:
    span.end()

# Traces sent to OpenTelemetry Collector automatically
```

## Examples

See `examples/` directory:

### Simple Tool (`examples/calculator.py`)
```python
from enum import Enum
from pydantic import BaseModel
from agentpack import tool, ExecutionContext

class Operation(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

class CalculatorInput(BaseModel):
    operation: Operation
    a: float
    b: float

class CalculatorOutput(BaseModel):
    result: float
    operation: str

@tool(
    name="calculator",
    description="Perform basic arithmetic operations",
    input_schema=CalculatorInput,
    output_schema=CalculatorOutput,
)
async def calculator(input: CalculatorInput, ctx: ExecutionContext) -> CalculatorOutput:
    # Pure business logic
    if input.operation == Operation.ADD:
        result = input.a + input.b
    elif input.operation == Operation.SUBTRACT:
        result = input.a - input.b
    elif input.operation == Operation.MULTIPLY:
        result = input.a * input.b
    elif input.operation == Operation.DIVIDE:
        if input.b == 0:
            raise ValueError("Division by zero")
        result = input.a / input.b

    return CalculatorOutput(
        result=result,
        operation=f"{input.a} {input.operation.value} {input.b}"
    )
```

### External API Tool (`examples/weather.py`)
Demonstrates:
- Secret management (`ctx.secrets.require()`)
- HTTP client with retries (`ctx.http.get()`)
- Structured logging
- Input validation with Pydantic

## API Reference

### `@tool` Decorator

Create a tool definition.

```python
from pydantic import BaseModel
from agentpack import tool, ExecutionContext

class MyInput(BaseModel):
    value: int

class MyOutput(BaseModel):
    result: int

@tool(
    name="my_tool",                    # Unique tool identifier
    description="My tool description", # Human-readable description
    input_schema=MyInput,              # Pydantic input model
    output_schema=MyOutput,            # Pydantic output model
)
async def my_tool(input: MyInput, ctx: ExecutionContext) -> MyOutput:
    return MyOutput(result=input.value * 2)
```

**Parameters**:
- `name` (str): Unique tool name
- `description` (str): Human-readable description
- `input_schema` (BaseModel): Pydantic input validation model
- `output_schema` (BaseModel): Pydantic output validation model

**Returns**: `Tool` instance (internal use by runtime)

## Error Handling

```python
from agentpack import (
    ToolError,
    ValidationError,
    SecretNotFoundError,
    HttpError,
)

async def my_handler(input: MyInput, ctx: ExecutionContext) -> MyOutput:
    # Validation errors raised automatically by Pydantic

    # Secret not found
    key = await ctx.secrets.require("API_KEY")  # raises SecretNotFoundError

    # HTTP errors from external APIs
    response = await ctx.http.get("...")  # raises HttpError on failure

    # Custom errors
    if not input.valid:
        raise ToolError("Invalid input", "INVALID_INPUT")
```

## Multi-File Tools

Tools can have dependencies:

```
tools/
├── calculator/
│   ├── __init__.py      # Entry point (exports tool)
│   ├── operations.py    # Helper functions
│   └── types.py         # Shared types
└── weather.py           # Single-file tool
```

**Builder discovers both patterns automatically**:
- Single-file: `tools/weather.py`
- Multi-file: `tools/calculator/__init__.py`

## Testing

```python
import pytest
from pydantic import BaseModel
from agentpack import tool, ExecutionContext

class TestInput(BaseModel):
    value: int

class TestOutput(BaseModel):
    result: int

@tool(
    name="test_tool",
    description="Test tool",
    input_schema=TestInput,
    output_schema=TestOutput,
)
async def test_tool(input: TestInput, ctx: ExecutionContext) -> TestOutput:
    return TestOutput(result=input.value * 2)

@pytest.mark.asyncio
async def test_my_tool():
    # Create mock context
    from agentpack.context import create_execution_context
    from agentpack.types import RequestMetadata

    metadata = RequestMetadata(request_id="123")
    ctx = create_execution_context(metadata)

    # Execute tool
    result = await test_tool.execute({"value": 5}, ctx)
    assert result.result == 10
```

## Deployment

**Nothing to do!** Builder + Runtime handle everything:

1. **Build**: `agentpack build` (or automatic via GitHub App)
2. **Deploy**: Automatic to Agentpack infrastructure
3. **Scale**: Automatic based on load
4. **Monitor**: Traces/logs in dashboard

### Configuration

Optional `agentpack.yaml` for advanced settings:

```yaml
version: 0.1
project: my-tools

agents:
  - name: default
    model: { provider: anthropic, name: claude-3-5-sonnet }
    tools: ["*"]  # All tools in tools/

resources:
  - name: stripe_secret
    type: secret
    source: vault://kv/stripe

policies:
  outbound_network:
    allow: ["*.stripe.com", "*.openai.com"]
```

## Thin SDK Philosophy

This SDK is **intentionally minimal**:
- ✅ `@tool` decorator for definitions
- ✅ `ExecutionContext` types
- ✅ Error classes
- ❌ NO server creation
- ❌ NO Docker setup
- ❌ NO deployment code

**All orchestration lives in Rust core** for:
- Consistent cross-language behavior
- Performance (Tower middleware)
- Security (policy enforcement)
- Observability (OpenTelemetry)

## Type Checking

The SDK is fully typed and works with mypy:

```bash
mypy tools/ --strict
```

## Troubleshooting

### "Tool not found" error
- Ensure tool is in `tools/` directory
- Check file exports tool with `@tool` decorator
- Verify `.agentpack-manifest.json` was generated

### Validation errors
- Check Pydantic model matches input
- Use `Optional[T]` or `= Field(default=...)` for optional fields
- Test with mock data

### Secret not found
- Configure secrets in Agentpack Dashboard
- Use correct secret key name
- Check environment variables in development

## Related Packages

- `agentpack-runtime-python` - Internal gRPC runtime (private)
- `@agentpack/sdk` - TypeScript SDK (same zero-config approach)

## License

MIT OR Apache-2.0
