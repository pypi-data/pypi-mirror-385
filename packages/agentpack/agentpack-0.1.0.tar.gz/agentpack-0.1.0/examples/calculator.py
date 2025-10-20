"""
Simple calculator example tool.

This demonstrates the ZERO-CONFIG approach:
- User writes ONLY business logic
- NO server setup, NO Docker, NO infrastructure
- Just define the tool - Builder + Runtime handle the rest
"""

from enum import Enum
from pydantic import BaseModel
from agentpack import ExecutionContext, tool


class Operation(str, Enum):
    """Arithmetic operations."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class CalculatorInput(BaseModel):
    """Calculator input schema."""

    operation: Operation
    a: float
    b: float


class CalculatorOutput(BaseModel):
    """Calculator output schema."""

    result: float
    operation: str


# THIS IS ALL THE USER WRITES - Just business logic!
@tool(
    name="calculator",
    description="Perform basic arithmetic operations",
    input_schema=CalculatorInput,
    output_schema=CalculatorOutput,
)
async def calculator(input: CalculatorInput, ctx: ExecutionContext) -> CalculatorOutput:
    """Calculate the result of an arithmetic operation."""
    ctx.logger.info(
        "Calculating",
        operation=input.operation.value,
        a=input.a,
        b=input.b,
    )

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
    else:
        raise ValueError(f"Unknown operation: {input.operation}")

    return CalculatorOutput(
        result=result,
        operation=f"{input.a} {input.operation.value} {input.b}",
    )


# That's it! No server code, no infrastructure.
# Builder will:
#   1. Scan tools/ directory
#   2. Find this file
#   3. Generate .agentpack-manifest.json
#   4. Build Docker image with runtime
#   5. Deploy to container backend
#
# Runtime will:
#   1. Load manifest
#   2. Import this tool
#   3. Start gRPC server
#   4. Handle requests from Rust core
