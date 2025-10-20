"""Entry point for running the MCP server via python -m vigil.mcp."""

from __future__ import annotations

import asyncio

from vigil.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
