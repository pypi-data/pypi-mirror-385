# Python Runtime Base Image
# This image provides the gRPC server that executes Python tools

FROM python:3.11-slim

WORKDIR /runtime

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy runtime package files
COPY pyproject.toml ./
COPY agentpack_runtime/ ./agentpack_runtime/

# Install the runtime
RUN pip install --no-cache-dir .

# Set up working directory for tools
WORKDIR /app

# Expose gRPC port
EXPOSE 50051

# Default command (tools will override this with their own manifest)
CMD ["agentpack-runtime"]
