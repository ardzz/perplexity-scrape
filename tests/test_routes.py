"""Tests for API routes with authentication."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def mock_perplexity_client():
    """Mock PerplexityClient to avoid actual API calls."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Test response"
    mock_response.citations = []
    mock_response.related_queries = []
    mock_response.media_items = []
    mock_client.ask.return_value = mock_response
    return mock_client


@pytest.fixture
async def app_with_auth():
    """Create test app with auth enabled."""
    with patch.dict("os.environ", {"API_KEY": "test-secret-key-123"}):
        # Need to reimport to pick up new env
        import importlib
        import src.config

        importlib.reload(src.config)

        from rest_api_service import app

        yield app


@pytest.fixture
async def app_without_auth():
    """Create test app with auth disabled."""
    with patch.dict("os.environ", {"API_KEY": ""}):
        import importlib
        import src.config

        importlib.reload(src.config)

        from rest_api_service import app

        yield app


class TestHealthEndpoint:
    """Tests for /health endpoint (should not require auth)."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self):
        """Health endpoint should return ok status."""
        from rest_api_service import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestModelsEndpointAuth:
    """Tests for /v1/models endpoint authentication."""

    @pytest.mark.asyncio
    async def test_models_without_auth_disabled(self):
        """When auth disabled, /v1/models should work without key."""
        with patch.dict("os.environ", {"API_KEY": ""}, clear=False):
            with patch("src.core.security.config") as mock_config:
                mock_config.auth_enabled = False

                from rest_api_service import app

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.get("/v1/models")

                assert response.status_code == 200
                data = response.json()
                assert "data" in data

    @pytest.mark.asyncio
    async def test_models_with_valid_key(self):
        """When auth enabled, /v1/models should work with valid key."""
        test_key = "test-secret-key-456"
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = test_key

            from rest_api_service import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/v1/models", headers={"X-API-Key": test_key}
                )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_models_without_key_when_auth_enabled(self):
        """When auth enabled, /v1/models without key should return 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            from rest_api_service import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/v1/models")

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_models_with_invalid_key(self):
        """When auth enabled, /v1/models with invalid key should return 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            from rest_api_service import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/v1/models", headers={"X-API-Key": "wrong-key"}
                )

            assert response.status_code == 401


class TestChatCompletionsEndpointAuth:
    """Tests for /v1/chat/completions endpoint authentication."""

    @pytest.mark.asyncio
    async def test_chat_completions_without_key_when_auth_enabled(self):
        """When auth enabled, chat completions without key should return 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            from rest_api_service import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/v1/chat/completions",
                    json={
                        "model": "claude-4.5-sonnet",
                        "messages": [{"role": "user", "content": "Hello"}],
                    },
                )

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_chat_completions_with_invalid_key(self):
        """When auth enabled, chat completions with invalid key should return 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            from rest_api_service import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/v1/chat/completions",
                    headers={"X-API-Key": "wrong-key"},
                    json={
                        "model": "claude-4.5-sonnet",
                        "messages": [{"role": "user", "content": "Hello"}],
                    },
                )

            assert response.status_code == 401
