# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Unit tests for the `mcp status` command.
"""

from typer.testing import CliRunner

from qbraid_cli.mcp.app import mcp_app, status

runner = CliRunner()


def test_status_command_output(capsys):
    """Test status command displays the expected placeholder message."""
    status()
    captured = capsys.readouterr()

    assert "MCP Status:" in captured.out
    assert "Implementation in progress..." in captured.out
    assert "This will show connection status for all configured MCP backends" in captured.out


def test_status_command_cli_integration():
    """Test mcp status command via CLI."""
    result = runner.invoke(mcp_app, ["status"])

    assert result.exit_code == 0
    assert "MCP Status:" in result.stdout
    assert "Implementation in progress..." in result.stdout


def test_status_command_no_errors():
    """Test status command runs without errors."""
    # Should not raise any exceptions
    status()


def test_status_command_cli_help():
    """Test mcp status command help."""
    result = runner.invoke(mcp_app, ["status", "--help"])

    assert result.exit_code == 0
    assert "status" in result.stdout.lower()
    assert (
        "Show status of MCP connections" in result.stdout or "connection" in result.stdout.lower()
    )
