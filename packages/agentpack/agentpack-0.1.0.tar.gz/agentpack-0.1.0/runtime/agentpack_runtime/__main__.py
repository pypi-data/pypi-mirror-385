"""Entry point for agentpack-runtime command."""

import asyncio
from .server import serve


def main():
    """Main entry point."""
    asyncio.run(serve())


if __name__ == "__main__":
    main()
