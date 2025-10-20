"""Tool definition API."""

from typing import Any, Callable, TypeVar, cast

from pydantic import BaseModel

from agentpack.types import ExecutionContext, Tool, ToolHandler

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


def tool(
    name: str,
    description: str,
    input_schema: type[TInput],
    output_schema: type[TOutput],
) -> Callable[[ToolHandler[TInput, TOutput]], Tool]:
    """
    Decorator to create a tool.

    Example:
        ```python
        from pydantic import BaseModel
        from agentpack import tool

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
    """

    def decorator(handler: ToolHandler[TInput, TOutput]) -> Tool:
        # Type-safe wrapper that handles validation
        async def wrapped_handler(input_data: Any, ctx: ExecutionContext) -> Any:
            # Input is already validated by Tool.execute()
            # Just call the handler
            return await handler(input_data, ctx)

        return Tool(
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            handler=wrapped_handler,
        )

    return decorator
