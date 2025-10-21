# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Unit tests for the `mcp list` command.
"""

from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from qbraid_cli.mcp.app import list_servers, mcp_app

runner = CliRunner()


def test_list_servers_success(capsys):
    """Test list_servers with available MCP servers."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="lab",
            base_url="https://lab.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="qBraid Lab MCP server",
        ),
        MCPServerEndpoint(
            name="lab-staging",
            base_url="https://lab-staging.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="qBraid Lab Staging MCP server",
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        list_servers(workspace="lab", include_staging=False)
        captured = capsys.readouterr()

        assert "Found 2 MCP server(s)" in captured.out
        assert "lab" in captured.out
        assert "https://lab.qbraid.com" in captured.out
        assert "qBraid Lab MCP server" in captured.out


def test_list_servers_no_servers_found(capsys):
    """Test list_servers when no MCP servers are found."""
    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=[]):
        list_servers(workspace="lab", include_staging=False)
        captured = capsys.readouterr()

        assert "No MCP servers found" in captured.out


def test_list_servers_with_staging(capsys):
    """Test list_servers with staging endpoints enabled."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="lab-staging",
            base_url="https://lab-staging.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="qBraid Lab Staging MCP server",
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        list_servers(workspace="lab", include_staging=True)
        captured = capsys.readouterr()

        assert "Found 1 MCP server(s)" in captured.out
        assert "lab-staging" in captured.out
        assert "https://lab-staging.qbraid.com" in captured.out


def test_list_servers_without_description(capsys):
    """Test list_servers with endpoints that have no description."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="test-server",
            base_url="https://test.qbraid.com",
            path_template="/mcp/test",
            description=None,
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        list_servers(workspace=None, include_staging=False)
        captured = capsys.readouterr()

        assert "Found 1 MCP server(s)" in captured.out
        assert "test-server" in captured.out
        assert "https://test.qbraid.com" in captured.out


def test_list_servers_import_error(capsys):
    """Test list_servers when qbraid-core MCP module is not available."""
    with patch("qbraid_core.services.mcp.discover_mcp_servers", side_effect=ImportError):
        with pytest.raises(typer.Exit) as exc_info:
            list_servers(workspace="lab", include_staging=False)

        assert exc_info.value.exit_code == 1
        captured = capsys.readouterr()
        assert "qbraid-core MCP module not found" in captured.out
        assert "pip install qbraid-core[mcp]" in captured.out


def test_list_servers_general_exception(capsys):
    """Test list_servers when an unexpected error occurs."""
    with patch(
        "qbraid_core.services.mcp.discover_mcp_servers", side_effect=RuntimeError("Test error")
    ):
        with pytest.raises(typer.Exit) as exc_info:
            list_servers(workspace="lab", include_staging=False)

        assert exc_info.value.exit_code == 1
        captured = capsys.readouterr()
        assert "Error listing MCP servers: Test error" in captured.out


def test_list_servers_cli_integration():
    """Test mcp list command via CLI."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="lab",
            base_url="https://lab.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="qBraid Lab MCP server",
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        result = runner.invoke(mcp_app, ["list"])

        assert result.exit_code == 0
        assert "Found 1 MCP server(s)" in result.stdout
        assert "lab" in result.stdout


def test_list_servers_cli_with_workspace():
    """Test mcp list command via CLI with workspace option."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="qbook",
            base_url="https://qbook.qbraid.com",
            path_template="/mcp/qbook",
            description="qBraid QBook MCP server",
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        result = runner.invoke(mcp_app, ["list", "--workspace", "qbook"])

        assert result.exit_code == 0
        assert "qbook" in result.stdout


def test_list_servers_cli_with_staging_flag():
    """Test mcp list command via CLI with staging flag."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="lab-staging",
            base_url="https://lab-staging.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="Staging server",
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        result = runner.invoke(mcp_app, ["list", "--staging"])

        assert result.exit_code == 0
        assert "lab-staging" in result.stdout


def test_list_servers_multiple_endpoints(capsys):
    """Test list_servers with multiple different endpoints."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    mock_endpoints = [
        MCPServerEndpoint(
            name="lab",
            base_url="https://lab.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="Lab MCP server",
        ),
        MCPServerEndpoint(
            name="devices",
            base_url="https://api.qbraid.com",
            path_template="/mcp/devices",
            description="Device catalog MCP server",
        ),
        MCPServerEndpoint(
            name="jobs",
            base_url="https://api.qbraid.com",
            path_template="/mcp/jobs",
            description="Job management MCP server",
        ),
    ]

    with patch("qbraid_core.services.mcp.discover_mcp_servers", return_value=mock_endpoints):
        list_servers(workspace=None, include_staging=False)
        captured = capsys.readouterr()

        assert "Found 3 MCP server(s)" in captured.out
        assert "lab" in captured.out
        assert "devices" in captured.out
        assert "jobs" in captured.out
