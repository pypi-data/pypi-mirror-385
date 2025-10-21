"""Vigil MCP (Machine-Callable Protocol) server.

This module provides a generic MCP server that exposes core Vigil verbs
to external AI assistants and automation tools.

Core verbs:
  - preview_data: Inspect data handles and return row samples
  - run_target: Execute Snakemake targets with dry-run validation
  - promote: Generate receipts from completed pipeline runs

Projects can extend the MCP server with custom domain-specific verbs.

Example:
    Start the MCP server from any Vigil project:
        $ vigil mcp serve

    The server runs via stdio and can be configured in Claude Desktop
    or other MCP-compatible clients.
"""

from vigil.mcp import server

__all__ = ["server"]
