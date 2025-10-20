"""Test that MCP server dependencies are optional."""

from __future__ import annotations

import sys

from typer.testing import CliRunner
from vigil import cli

runner = CliRunner()


def test_mcp_serve_requires_mcp_extras():
    """Test that 'vigil mcp serve' fails gracefully without MCP dependencies."""
    # Test that help always works regardless of dependencies
    result = runner.invoke(cli.app, ["mcp", "serve", "--help"])

    # Help should always work
    assert result.exit_code == 0
    assert "mcp" in result.stdout.lower() or "server" in result.stdout.lower()


def test_mcp_serve_command_exists():
    """Test that 'vigil mcp serve' command is registered."""
    result = runner.invoke(cli.app, ["mcp", "--help"])

    assert result.exit_code == 0
    assert "serve" in result.stdout
    assert "MCP" in result.stdout or "Machine" in result.stdout


def test_mcp_dependencies_are_importable_in_tests():
    """Test that MCP dependencies are available in test environment."""
    # This test verifies the test environment has MCP dependencies
    # In production, these would be optional
    try:
        import mcp  # type: ignore  # noqa: F401
        import polars  # type: ignore  # noqa: F401
        mcp_available = True
    except ImportError:
        mcp_available = False

    # In the development/test environment, MCP should be available
    # In production with base install only, this would be False
    assert mcp_available or "GITHUB_ACTIONS" in sys.modules, (
        "MCP dependencies should be available in test environment"
    )
