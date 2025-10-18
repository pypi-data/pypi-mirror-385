"""Tests for MCP transports."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from msgflux.protocols.mcp.exceptions import MCPConnectionError, MCPError, MCPTimeoutError
from msgflux.protocols.mcp.transports import HTTPTransport, StdioTransport


class TestHTTPTransport:
    """Tests for HTTPTransport."""

    @pytest.mark.asyncio
    async def test_init(self):
        """Test HTTPTransport initialization."""
        transport = HTTPTransport(
            base_url="http://localhost:8080",
            timeout=30.0,
            headers={"Authorization": "Bearer token"}
        )

        assert transport.base_url == "http://localhost:8080"
        assert transport.timeout == 30.0
        assert transport.headers["Authorization"] == "Bearer token"

    @pytest.mark.asyncio
    async def test_init_with_pool_limits(self):
        """Test initialization with custom pool limits."""
        transport = HTTPTransport(
            base_url="http://localhost:8080",
            pool_limits={"max_connections": 50, "max_keepalive_connections": 10}
        )

        assert transport.pool_limits["max_connections"] == 50
        assert transport.pool_limits["max_keepalive_connections"] == 10

    @pytest.mark.asyncio
    async def test_init_defaults_pool_limits(self):
        """Test default pool limits."""
        transport = HTTPTransport(base_url="http://localhost:8080")

        assert transport.pool_limits["max_connections"] == 100
        assert transport.pool_limits["max_keepalive_connections"] == 20

    @pytest.mark.asyncio
    @patch("msgflux.protocols.mcp.transports.HTTPX_AVAILABLE", True)
    @patch("msgflux.protocols.mcp.transports.httpx")
    async def test_connect(self, mock_httpx):
        """Test connecting creates AsyncClient."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        transport = HTTPTransport(base_url="http://localhost:8080")
        await transport.connect()

        assert transport._http_client is not None
        mock_httpx.AsyncClient.assert_called_once()

    @pytest.mark.asyncio
    @patch("msgflux.protocols.mcp.transports.HTTPX_AVAILABLE", True)
    @patch("msgflux.protocols.mcp.transports.httpx")
    async def test_send_request(self, mock_httpx):
        """Test sending JSON-RPC request."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "id": "1", "result": {"tools": []}}
        mock_client.post.return_value = mock_response

        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        transport = HTTPTransport(base_url="http://localhost:8080")
        await transport.connect()

        result = await transport.send_request("tools/list", {"param": "value"})

        assert "result" in result
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "http://localhost:8080/" in call_args[0]

    @pytest.mark.asyncio
    @patch("msgflux.protocols.mcp.transports.HTTPX_AVAILABLE", True)
    @patch("msgflux.protocols.mcp.transports.httpx")
    async def test_send_notification(self, mock_httpx):
        """Test sending notification (fire-and-forget)."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        transport = HTTPTransport(base_url="http://localhost:8080")
        await transport.connect()

        # Should not raise even if it fails
        await transport.send_notification("test/notify", {"data": "value"})

        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    @patch("msgflux.protocols.mcp.transports.HTTPX_AVAILABLE", True)
    @patch("msgflux.protocols.mcp.transports.httpx")
    async def test_disconnect(self, mock_httpx):
        """Test disconnect closes client."""
        mock_client = AsyncMock()
        mock_httpx.AsyncClient.return_value = mock_client
        mock_httpx.Timeout = MagicMock()
        mock_httpx.Limits = MagicMock()

        transport = HTTPTransport(base_url="http://localhost:8080")
        await transport.connect()
        await transport.disconnect()

        mock_client.aclose.assert_called_once()
        assert transport._http_client is None


class TestStdioTransport:
    """Tests for StdioTransport."""

    def test_init(self):
        """Test StdioTransport initialization."""
        transport = StdioTransport(
            command="mcp-server",
            args=["--arg1", "value1"],
            cwd="/workspace",
            timeout=30.0
        )

        assert transport.command == "mcp-server"
        assert transport.args == ["--arg1", "value1"]
        assert transport.cwd == "/workspace"
        assert transport.timeout == 30.0

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_connect(self, mock_subprocess):
        """Test connecting launches subprocess."""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_subprocess.return_value = mock_process

        transport = StdioTransport(command="test-command")
        await transport.connect()

        assert transport._process is not None
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_send_request(self, mock_subprocess):
        """Test sending request via stdin."""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        # Mock stdout to return a response
        response_data = {"jsonrpc": "2.0", "id": "1", "result": {"success": True}}
        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(response_data) + "\n").encode("utf-8")
        )

        mock_subprocess.return_value = mock_process

        transport = StdioTransport(command="test-command", timeout=5.0)
        await transport.connect()

        # Give time for read task to start
        await asyncio.sleep(0.1)

        result = await transport.send_request("test/method", {"param": "value"})

        assert "result" in result
        assert result["result"]["success"] is True
        mock_process.stdin.write.assert_called()

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_send_notification(self, mock_subprocess):
        """Test sending notification via stdin."""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_subprocess.return_value = mock_process

        transport = StdioTransport(command="test-command")
        await transport.connect()

        await transport.send_notification("test/notify", {"data": "value"})

        mock_process.stdin.write.assert_called()
        # Notification should not have "id" field
        call_data = mock_process.stdin.write.call_args[0][0]
        message = json.loads(call_data.decode("utf-8"))
        assert "id" not in message

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_disconnect(self, mock_subprocess):
        """Test disconnect terminates subprocess."""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock()
        mock_subprocess.return_value = mock_process

        transport = StdioTransport(command="test-command")
        await transport.connect()
        await transport.disconnect()

        mock_process.terminate.assert_called_once()
        assert transport._process is None

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_connect_failure(self, mock_subprocess):
        """Test connection failure raises MCPConnectionError."""
        mock_subprocess.side_effect = Exception("Failed to start process")

        transport = StdioTransport(command="invalid-command")

        with pytest.raises(MCPConnectionError):
            await transport.connect()

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_request_timeout(self, mock_subprocess):
        """Test request timeout raises MCPTimeoutError."""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        # stdout never returns a response (simulates timeout)
        async def never_return():
            await asyncio.sleep(100)  # Long delay
            return b""

        mock_process.stdout.readline = never_return
        mock_subprocess.return_value = mock_process

        transport = StdioTransport(command="test-command", timeout=0.1)
        await transport.connect()

        with pytest.raises(MCPTimeoutError):
            await transport.send_request("test/method")

    @pytest.mark.asyncio
    async def test_send_request_not_connected(self):
        """Test sending request when not connected raises error."""
        transport = StdioTransport(command="test-command")

        with pytest.raises(MCPConnectionError):
            await transport.send_request("test/method")
