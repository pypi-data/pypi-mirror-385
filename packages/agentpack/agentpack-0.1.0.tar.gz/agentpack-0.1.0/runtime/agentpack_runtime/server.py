"""gRPC server implementation for Python tools."""

import asyncio
import json
import logging
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any
from concurrent import futures

import grpc
from google.protobuf import empty_pb2
from google.protobuf import struct_pb2

# Import generated proto stubs
from agentpack_runtime.gen.agentpack.v1 import tool_pb2_grpc
from agentpack_runtime.gen.agentpack.types import tool_spec_pb2
from agentpack_runtime.gen.agentpack.types import common_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolHostServicer(tool_pb2_grpc.ToolHostServicer):
    """Implements the ToolHost gRPC service."""

    def __init__(self):
        super().__init__()
        self.tools: Dict[str, Any] = {}
        self._load_tools_from_manifest()

    def _load_tools_from_manifest(self):
        """Load tools from .agentpack-manifest.json"""
        manifest_path = Path.cwd() / ".agentpack-manifest.json"

        if not manifest_path.exists():
            logger.warning(f"No manifest found at {manifest_path}")
            return

        with open(manifest_path) as f:
            manifest = json.load(f)

        logger.info(f"Loading {len(manifest['tools'])} tools from manifest")

        for entry in manifest["tools"]:
            tool_name = entry["name"]
            tool_path = entry["path"]
            export_name = entry.get("export", "default")

            # Convert /app/ path to actual filesystem path
            # In container, /app is the working directory
            abs_path = Path(tool_path)
            if not abs_path.exists():
                # Try relative to cwd
                abs_path = Path.cwd() / tool_path.lstrip("/app/")

            logger.info(f"Loading tool '{tool_name}' from {abs_path}")

            try:
                # Dynamically import the module
                spec = importlib.util.spec_from_file_location(tool_name, abs_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[tool_name] = module
                    spec.loader.exec_module(module)

                    # Get the tool (default export or named)
                    if export_name == "default" and hasattr(module, "default"):
                        tool = module.default
                    elif export_name == "default" and hasattr(module, tool_name):
                        tool = getattr(module, tool_name)
                    else:
                        tool = getattr(module, export_name)

                    self.tools[tool_name] = tool
                    logger.info(f"Loaded tool: {tool_name}")
                else:
                    logger.error(f"Failed to load spec for {tool_name}")
            except Exception as e:
                logger.error(f"Failed to load tool {tool_name}: {e}", exc_info=True)

        logger.info(f"Loaded {len(self.tools)} tools total")

    async def Describe(self, request, context):
        """Return tool specifications."""
        logger.info("Describe called")

        # For MVP, return spec for first tool
        # TODO: Support multiple tools per container
        if not self.tools:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("No tools loaded")
            return tool_spec_pb2.ToolSpec()

        tool_name = list(self.tools.keys())[0]
        tool = self.tools[tool_name]

        # Build ToolSpec from SDK tool definition
        spec = tool_spec_pb2.ToolSpec()
        spec.name = getattr(tool, 'name', tool_name)
        spec.description = getattr(tool, 'description', '')
        spec.language = "python"

        # Convert schemas to protobuf Struct
        # SDK tools have input_schema and output_schema as Pydantic models
        # We need to convert them to JSON Schema format
        if hasattr(tool, 'input_schema'):
            # TODO: Convert Pydantic model to JSON Schema
            pass

        return spec

    async def Invoke(self, request, context):
        """Invoke a tool with given arguments."""
        # Extract tool name from ToolRequest
        tool_name = request.tool.name if request.HasField('tool') else None

        if not tool_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Missing tool name in request")
            return common_pb2.ToolResult()

        logger.info(f"Invoking tool: {tool_name}")

        if tool_name not in self.tools:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Tool not found: {tool_name}")
            return common_pb2.ToolResult()

        tool = self.tools[tool_name]

        try:
            # Convert protobuf Struct args to Python dict
            from google.protobuf.json_format import MessageToDict
            args = MessageToDict(request.args) if request.HasField('args') else {}

            logger.info(f"Tool arguments: {args}")

            # Create execution context (simplified for now)
            # TODO: Populate from request.context
            ctx = type('Context', (), {
                'logger': logger,
                'secrets': {},
                'http': {}
            })()

            # Call the tool's execute method (SDK pattern)
            if hasattr(tool, 'execute'):
                result = await tool.execute(args, ctx)
            elif callable(tool):
                result = await tool(args, ctx)
            else:
                raise ValueError(f"Tool {tool_name} is not callable")

            logger.info(f"Tool {tool_name} returned: {result}")

            # Convert result to protobuf ToolResult
            tool_result = common_pb2.ToolResult()

            # Convert Python dict to protobuf Struct
            from google.protobuf.json_format import ParseDict
            if isinstance(result, dict):
                ParseDict(result, tool_result.output)
            else:
                # Wrap non-dict results
                ParseDict({"value": result}, tool_result.output)

            return tool_result

        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return common_pb2.ToolResult()

    async def InvokeStream(self, request, context):
        """Invoke a tool with streaming response."""
        # TODO: Implement streaming
        logger.warning("InvokeStream not yet implemented")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        return


async def serve():
    """Start the gRPC server."""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register the ToolHost service
    tool_pb2_grpc.add_ToolHostServicer_to_server(ToolHostServicer(), server)

    listen_addr = "0.0.0.0:50051"
    server.add_insecure_port(listen_addr)

    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop(grace=5.0)
