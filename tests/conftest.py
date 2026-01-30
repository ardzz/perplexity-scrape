"""Pytest fixtures for test suite."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture
def auth_enabled_config():
    """Fixture providing config with auth enabled."""
    with patch.dict(os.environ, {"API_KEY": "test-secret-key-123"}, clear=False):
        # Re-import to get fresh config with env var
        from src.config import Config

        yield Config.from_env()


@pytest.fixture
def auth_disabled_config():
    """Fixture providing config with auth disabled."""
    with patch.dict(os.environ, {"API_KEY": ""}, clear=False):
        from src.config import Config

        yield Config.from_env()


@pytest.fixture
def test_api_key():
    """Return a test API key."""
    return "test-secret-key-123"


@pytest.fixture
def client():
    """Create a test client for FastAPI app."""
    from httpx import AsyncClient, ASGITransport
    from rest_api_service import app

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
