"""Tests for MCP HTTP transport with authentication."""

import pytest
from unittest.mock import patch, MagicMock
from contextlib import asynccontextmanager
from httpx import AsyncClient, ASGITransport


class TestMCPAuthMiddleware:
    """Unit tests for MCP authentication middleware."""

    @pytest.mark.asyncio
    async def test_middleware_allows_request_when_auth_disabled(self):
        """When auth is disabled, middleware should allow all requests."""
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse

        async def dummy_endpoint(request):
            return JSONResponse({"status": "ok"})

        app = Starlette(routes=[Route("/test", dummy_endpoint)])

        with patch("src.core.mcp_auth.config") as mock_config:
            mock_config.auth_enabled = False

            from src.core.mcp_auth import MCPAuthMiddleware

            app.add_middleware(MCPAuthMiddleware)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/test")

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_middleware_rejects_missing_key_when_auth_enabled(self):
        """When auth is enabled, requests without API key should be rejected."""
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse

        async def dummy_endpoint(request):
            return JSONResponse({"status": "ok"})

        app = Starlette(routes=[Route("/test", dummy_endpoint)])

        with patch("src.core.mcp_auth.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-secret-key"

            from src.core.mcp_auth import MCPAuthMiddleware

            app.add_middleware(MCPAuthMiddleware)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/test")

            assert response.status_code == 401
            data = response.json()
            assert data["jsonrpc"] == "2.0"
            assert data["error"]["code"] == -32001
            assert "Missing API key" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_middleware_rejects_invalid_key(self):
        """When auth is enabled, requests with invalid API key should be rejected."""
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse

        async def dummy_endpoint(request):
            return JSONResponse({"status": "ok"})

        app = Starlette(routes=[Route("/test", dummy_endpoint)])

        with patch("src.core.mcp_auth.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-secret-key"

            from src.core.mcp_auth import MCPAuthMiddleware

            app.add_middleware(MCPAuthMiddleware)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/test", headers={"X-API-Key": "wrong-key"})

            assert response.status_code == 401
            data = response.json()
            assert data["jsonrpc"] == "2.0"
            assert data["error"]["code"] == -32001
            assert "Invalid API key" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_middleware_allows_valid_key(self):
        """When auth is enabled, requests with valid API key should be allowed."""
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import JSONResponse

        async def dummy_endpoint(request):
            return JSONResponse({"status": "ok"})

        app = Starlette(routes=[Route("/test", dummy_endpoint)])

        valid_key = "valid-secret-key"
        with patch("src.core.mcp_auth.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = valid_key

            from src.core.mcp_auth import MCPAuthMiddleware

            app.add_middleware(MCPAuthMiddleware)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/test", headers={"X-API-Key": valid_key})

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}


class TestMCPHTTPAppCreation:
    """Tests for MCP HTTP app creation."""

    def test_streamable_http_app_returns_starlette(self):
        """streamable_http_app() should return a Starlette application."""
        from mcp_service import mcp
        from starlette.applications import Starlette

        app = mcp.streamable_http_app()

        assert isinstance(app, Starlette)

    def test_streamable_http_app_has_mcp_route(self):
        """The app should have the /mcp route."""
        from mcp_service import mcp

        app = mcp.streamable_http_app()
        route_paths = [route.path for route in app.routes]

        assert "/mcp" in route_paths

    def test_middleware_can_be_added(self):
        """Middleware should be addable to the app."""
        from mcp_service import mcp
        from src.core.mcp_auth import MCPAuthMiddleware

        app = mcp.streamable_http_app()

        # This should not raise
        app.add_middleware(MCPAuthMiddleware)

        # Verify the app is still functional (has routes)
        assert len(app.routes) > 0


class TestMCPHTTPConfig:
    """Tests for MCP HTTP configuration."""

    def test_mcp_transport_mode_default_is_stdio(self):
        """Default transport mode should be stdio."""
        with patch.dict("os.environ", {}, clear=False):
            # Remove any existing MCP_TRANSPORT_MODE
            import os

            os.environ.pop("MCP_TRANSPORT_MODE", None)

            import importlib
            import src.config

            importlib.reload(src.config)

            assert src.config.config.mcp_transport_mode == "stdio"

    def test_mcp_transport_mode_can_be_http(self):
        """Transport mode should be configurable to http."""
        with patch.dict("os.environ", {"MCP_TRANSPORT_MODE": "http"}):
            import importlib
            import src.config

            importlib.reload(src.config)

            assert src.config.config.mcp_transport_mode == "http"

    def test_mcp_http_host_default(self):
        """Default HTTP host should be 127.0.0.1."""
        with patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("MCP_HTTP_HOST", None)

            import importlib
            import src.config

            importlib.reload(src.config)

            assert src.config.config.mcp_http_host == "127.0.0.1"

    def test_mcp_http_port_default(self):
        """Default HTTP port should be 8000."""
        with patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("MCP_HTTP_PORT", None)

            import importlib
            import src.config

            importlib.reload(src.config)

            assert src.config.config.mcp_http_port == 8000
