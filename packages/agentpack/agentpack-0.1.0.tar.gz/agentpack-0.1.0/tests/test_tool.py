"""Smoke tests for Agentpack Python SDK"""
import pytest
from pydantic import BaseModel
from agentpack import tool, Tool


class EchoInput(BaseModel):
    """Input schema for echo tool"""
    message: str


class EchoOutput(BaseModel):
    """Output schema for echo tool"""
    result: str


class CalculatorInput(BaseModel):
    """Input schema for calculator"""
    a: float
    b: float
    operation: str


class CalculatorOutput(BaseModel):
    """Output schema for calculator"""
    result: float


def test_tool_decorator_basic():
    """Test that tool decorator works with basic schemas"""
    from agentpack import ExecutionContext

    @tool(
        name="echo-tool",
        description="A simple echo tool",
        input_schema=EchoInput,
        output_schema=EchoOutput,
    )
    async def echo(input: EchoInput, ctx: ExecutionContext) -> EchoOutput:
        return EchoOutput(result=input.message)

    # The decorator returns a Tool instance
    assert isinstance(echo, Tool)
    assert echo.name == "echo-tool"
    assert echo.description == "A simple echo tool"


def test_input_validation():
    """Test that Pydantic validates input"""
    # Valid input
    valid = EchoInput(message="hello")
    assert valid.message == "hello"

    # Invalid input (missing field)
    with pytest.raises(Exception):  # Pydantic ValidationError
        EchoInput()  # type: ignore


def test_output_validation():
    """Test that Pydantic validates output"""
    # Valid output
    valid = EchoOutput(result="world")
    assert valid.result == "world"

    # Invalid output (missing field)
    with pytest.raises(Exception):  # Pydantic ValidationError
        EchoOutput()  # type: ignore


def test_sdk_imports():
    """Test that main SDK exports are available"""
    from agentpack import tool, ExecutionContext, Tool

    assert tool is not None
    assert ExecutionContext is not None
    assert Tool is not None
    assert callable(tool)
