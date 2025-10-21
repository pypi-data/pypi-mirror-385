# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Unit tests for the `mcp serve` command and MCPAggregatorServer.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import typer

from qbraid_cli.mcp.serve import MCPAggregatorServer, serve_mcp


@pytest.fixture
def mock_session():
    """Create a mock QbraidSession."""
    session = MagicMock()
    session.get_user.return_value = {"email": "test@example.com"}
    session.api_key = "test-api-key"
    session.get_jupyter_token_data.return_value = {
        "user": "jovyan@example.com",
        "id": "a24960",
        "kind": "api_token",
        "roles": [],
        "scopes": ["servers", "read:services", "tokens"],
        "created": "2025-10-20T21:46:34.040146Z",
        "last_activity": None,
        "expires_at": None,
        "note": "Requested via api by user api-service",
        "session_id": None,
        "oauth_client": "JupyterHub",
        "token": "test-jupyter-token",
    }
    return session


@pytest.fixture
def mock_endpoints():
    """Create mock MCP server endpoints."""
    from qbraid_core.services.mcp.discovery import MCPServerEndpoint

    return [
        MCPServerEndpoint(
            name="lab",
            base_url="https://lab.qbraid.com",
            path_template="/user/{username}/mcp/mcp",
            description="Lab MCP server",
        ),
    ]


@pytest.fixture
def mock_router():
    """Create a mock MCPRouter."""
    router = MagicMock()
    router.connect_all = AsyncMock()
    router.get_connected_backends.return_value = ["lab"]
    router.handle_message = AsyncMock()
    router.shutdown_all = AsyncMock()
    return router


@pytest.fixture
def mock_client():
    """Create a mock MCPWebSocketClient."""
    client = MagicMock()
    client.is_connected = True
    return client


class TestMCPAggregatorServer:
    """Tests for MCPAggregatorServer class."""

    def test_init(self, mock_session):
        """Test MCPAggregatorServer initialization."""
        server = MCPAggregatorServer(
            session=mock_session, workspace="lab", include_staging=False, debug=True
        )

        assert server.session == mock_session
        assert server.workspace == "lab"
        assert server.include_staging is False
        assert server.debug is True
        assert server.router is None

    @pytest.mark.asyncio
    async def test_initialize_backends_success(self, mock_session, mock_endpoints, mock_router):
        """Test successful backend initialization."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab", debug=False)

        with (
            patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=mock_endpoints),
            patch("qbraid_cli.mcp.serve.MCPRouter", return_value=mock_router),
            patch("qbraid_cli.mcp.serve.MCPWebSocketClient") as mock_ws_client_class,
        ):
            mock_ws_client = MagicMock()
            mock_ws_client_class.return_value = mock_ws_client

            await server.initialize_backends()

            # Verify session.get_user was called
            mock_session.get_user.assert_called_once()

            # Verify router was created and connected
            assert server.router is not None
            mock_router.connect_all.assert_called_once()
            mock_router.get_connected_backends.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_backends_user_info_error(self, mock_session):
        """Test backend initialization when user info retrieval fails."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        mock_session.get_user.side_effect = RuntimeError("User info error")

        with pytest.raises(typer.Exit) as exc_info:
            await server.initialize_backends()

        assert exc_info.value.exit_code == 1

    @pytest.mark.asyncio
    async def test_initialize_backends_no_email(self, mock_session):
        """Test backend initialization when user email is missing."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        mock_session.get_user.return_value = {}  # No email

        with pytest.raises(typer.Exit) as exc_info:
            await server.initialize_backends()

        assert exc_info.value.exit_code == 1

    @pytest.mark.asyncio
    async def test_initialize_backends_no_auth_token(self, mock_session, mock_endpoints, capsys):
        """Test backend initialization when jupyter token retrieval fails for lab endpoints."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        mock_session.get_jupyter_token_data.side_effect = RuntimeError("No token available")

        with (
            patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=mock_endpoints),
            patch("qbraid_cli.mcp.serve.MCPRouter") as mock_router_class,
        ):
            mock_router = MagicMock()
            mock_router_class.return_value = mock_router

            # Now expects typer.Exit(1) with proper error handling
            with pytest.raises(typer.Exit) as exc_info:
                await server.initialize_backends()

            assert exc_info.value.exit_code == 1
            captured = capsys.readouterr()
            assert "Could not retrieve Jupyter token" in captured.err

    @pytest.mark.asyncio
    async def test_initialize_backends_no_endpoints(self, mock_session):
        """Test backend initialization when no endpoints are discovered."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")

        with patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=[]):
            with pytest.raises(typer.Exit) as exc_info:
                await server.initialize_backends()

            assert exc_info.value.exit_code == 1

    @pytest.mark.asyncio
    async def test_initialize_backends_connection_failure(
        self, mock_session, mock_endpoints, mock_router
    ):
        """Test backend initialization when connection fails."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        mock_router.get_connected_backends.return_value = []  # No connections

        with (
            patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=mock_endpoints),
            patch("qbraid_cli.mcp.serve.MCPRouter", return_value=mock_router),
            patch("qbraid_cli.mcp.serve.MCPWebSocketClient"),
        ):
            with pytest.raises(typer.Exit) as exc_info:
                await server.initialize_backends()

            assert exc_info.value.exit_code == 1

    @pytest.mark.asyncio
    async def test_initialize_backends_skip_lab_without_jupyter_token(
        self, mock_session, mock_endpoints, mock_router, capsys
    ):
        """Test that lab endpoints fail gracefully when jupyter token data is unavailable."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        mock_session.get_jupyter_token_data.side_effect = RuntimeError("No token available")

        with (
            patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=mock_endpoints),
            patch("qbraid_cli.mcp.serve.MCPRouter", return_value=mock_router),
            patch("qbraid_cli.mcp.serve.MCPWebSocketClient") as mock_ws_client_class,
        ):
            # Should raise typer.Exit(1) with proper error message
            with pytest.raises(typer.Exit) as exc_info:
                await server.initialize_backends()

            assert exc_info.value.exit_code == 1
            captured = capsys.readouterr()
            assert "Could not retrieve Jupyter token" in captured.err

            # Verify WebSocket client was not created
            mock_ws_client_class.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_backends_missing_token_in_data(
        self, mock_session, mock_endpoints, mock_router, capsys
    ):
        """Test that lab endpoints fail when token key is missing from response data."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        # Return data without 'token' key
        mock_session.get_jupyter_token_data.return_value = {"user": "test@example.com"}

        with (
            patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=mock_endpoints),
            patch("qbraid_cli.mcp.serve.MCPRouter", return_value=mock_router),
            patch("qbraid_cli.mcp.serve.MCPWebSocketClient") as mock_ws_client_class,
        ):
            # Should raise typer.Exit(1) with proper error message
            with pytest.raises(typer.Exit) as exc_info:
                await server.initialize_backends()

            assert exc_info.value.exit_code == 1
            captured = capsys.readouterr()
            assert "Could not retrieve Jupyter token" in captured.err

            # Verify WebSocket client was not created
            mock_ws_client_class.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_backends_no_api_key_for_non_lab(
        self, mock_session, mock_router, capsys
    ):
        """Test that non-lab endpoints fail when API key is not available."""
        from qbraid_core.services.mcp.discovery import MCPServerEndpoint

        non_lab_endpoint = MCPServerEndpoint(
            name="qbook",
            base_url="https://qbook.qbraid.com",
            path_template="/mcp/{username}",
            description="QBook MCP server",
        )

        server = MCPAggregatorServer(session=mock_session, workspace="qbook")
        mock_session.api_key = None  # No API key

        with (
            patch("qbraid_cli.mcp.serve.discover_mcp_servers", return_value=[non_lab_endpoint]),
            patch("qbraid_cli.mcp.serve.MCPRouter", return_value=mock_router),
            patch("qbraid_cli.mcp.serve.MCPWebSocketClient") as mock_ws_client_class,
        ):
            # Should raise typer.Exit(1) with proper error message
            with pytest.raises(typer.Exit) as exc_info:
                await server.initialize_backends()

            assert exc_info.value.exit_code == 1
            captured = capsys.readouterr()
            assert "No API key available" in captured.err

            # Verify WebSocket client was not created
            mock_ws_client_class.assert_not_called()

    def test_handle_backend_message_success(self, mock_session):
        """Test handling backend messages successfully."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        test_message = {"method": "test", "result": "success"}

        with patch("sys.stdout") as mock_stdout:
            mock_stdout.write = MagicMock()
            mock_stdout.flush = MagicMock()

            server._handle_backend_message(test_message)

            # Verify message was written to stdout
            mock_stdout.write.assert_called()
            call_args = mock_stdout.write.call_args[0][0]
            assert '"method": "test"' in call_args
            assert '"result": "success"' in call_args

    def test_handle_backend_message_json_error(self, mock_session):
        """Test handling backend messages when JSON serialization fails."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")

        # Create an object that can't be serialized to JSON
        class UnserializableObject:
            pass

        test_message = {"data": UnserializableObject()}

        # Should not raise, just log the error
        server._handle_backend_message(test_message)

    def test_shutdown_event_initially_not_set(self, mock_session):
        """Test that shutdown event is initially not set."""
        server = MCPAggregatorServer(session=mock_session, workspace="lab")
        assert not server._shutdown_event.is_set()


class TestServeMCP:
    """Tests for serve_mcp function."""

    def test_serve_mcp_session_creation_error(self, capsys):
        """Test serve_mcp when session creation fails."""
        with patch("qbraid_cli.mcp.serve.QbraidSession", side_effect=RuntimeError("Session error")):
            with pytest.raises(typer.Exit) as exc_info:
                serve_mcp(workspace="lab", include_staging=False, debug=False)

            assert exc_info.value.exit_code == 1
            captured = capsys.readouterr()
            assert "Session error" in captured.err

    def test_serve_mcp_keyboard_interrupt(self, mock_session):
        """Test serve_mcp handling KeyboardInterrupt."""
        with (
            patch("qbraid_cli.mcp.serve.QbraidSession", return_value=mock_session),
            patch("qbraid_cli.mcp.serve.MCPAggregatorServer") as mock_server_class,
            patch("asyncio.run", side_effect=KeyboardInterrupt),
        ):
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            # Should not raise, just log and exit gracefully
            serve_mcp(workspace="lab", include_staging=False, debug=False)

    def test_serve_mcp_runtime_error(self, mock_session, capsys):
        """Test serve_mcp handling runtime errors."""
        with (
            patch("qbraid_cli.mcp.serve.QbraidSession", return_value=mock_session),
            patch("qbraid_cli.mcp.serve.MCPAggregatorServer") as mock_server_class,
            patch("asyncio.run", side_effect=RuntimeError("Test error")),
        ):
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            with pytest.raises(typer.Exit) as exc_info:
                serve_mcp(workspace="lab", include_staging=False, debug=False)

            assert exc_info.value.exit_code == 1
            captured = capsys.readouterr()
            assert "Test error" in captured.err

    def test_serve_mcp_debug_mode(self, mock_session):
        """Test serve_mcp with debug mode enabled."""
        with (
            patch("qbraid_cli.mcp.serve.QbraidSession", return_value=mock_session),
            patch("qbraid_cli.mcp.serve.MCPAggregatorServer") as mock_server_class,
            patch("asyncio.run", side_effect=KeyboardInterrupt),
        ):
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            serve_mcp(workspace="lab", include_staging=False, debug=True)

            # Verify server was created with debug=True
            mock_server_class.assert_called_once()
            call_kwargs = mock_server_class.call_args[1]
            assert call_kwargs["debug"] is True

    def test_serve_mcp_staging_mode(self, mock_session):
        """Test serve_mcp with staging endpoints enabled."""
        with (
            patch("qbraid_cli.mcp.serve.QbraidSession", return_value=mock_session),
            patch("qbraid_cli.mcp.serve.MCPAggregatorServer") as mock_server_class,
            patch("asyncio.run", side_effect=KeyboardInterrupt),
        ):
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            serve_mcp(workspace="lab", include_staging=True, debug=False)

            # Verify server was created with include_staging=True
            mock_server_class.assert_called_once()
            call_kwargs = mock_server_class.call_args[1]
            assert call_kwargs["include_staging"] is True

    def test_serve_mcp_custom_workspace(self, mock_session):
        """Test serve_mcp with custom workspace."""
        with (
            patch("qbraid_cli.mcp.serve.QbraidSession", return_value=mock_session),
            patch("qbraid_cli.mcp.serve.MCPAggregatorServer") as mock_server_class,
            patch("asyncio.run", side_effect=KeyboardInterrupt),
        ):
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            serve_mcp(workspace="qbook", include_staging=False, debug=False)

            # Verify server was created with workspace="qbook"
            mock_server_class.assert_called_once()
            call_kwargs = mock_server_class.call_args[1]
            assert call_kwargs["workspace"] == "qbook"
