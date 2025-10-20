"""Package entry point for launching the MCP server via ``python -m``."""

from __future__ import annotations

import asyncio

from .server import main


def run() -> None:
    """Synchronously run the MCP server."""

    asyncio.run(main())


if __name__ == "__main__":
    run()
