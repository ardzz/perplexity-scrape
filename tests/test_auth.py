"""Tests for API key authentication."""

import pytest
import secrets
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from src.core.security import verify_api_key, api_key_header


class TestVerifyApiKey:
    """Tests for verify_api_key function."""

    def test_auth_disabled_no_key_passes(self):
        """When auth disabled (empty API_KEY), requests without key should pass."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = False
            mock_config.api_key = ""

            result = verify_api_key(api_key=None)
            assert result is None

    def test_auth_disabled_with_key_passes(self):
        """When auth disabled, requests with any key should still pass."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = False
            mock_config.api_key = ""

            result = verify_api_key(api_key="any-random-key")
            assert result is None

    def test_auth_enabled_valid_key_passes(self):
        """When auth enabled, valid API key should pass."""
        test_key = "valid-secret-key-123"
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = test_key

            result = verify_api_key(api_key=test_key)
            assert result == test_key

    def test_auth_enabled_missing_key_raises_401(self):
        """When auth enabled, missing key should raise 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key=None)

            assert exc_info.value.status_code == 401
            assert "Missing API key" in exc_info.value.detail

    def test_auth_enabled_empty_key_raises_401(self):
        """When auth enabled, empty string key should raise 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key="")

            assert exc_info.value.status_code == 401
            assert "Missing API key" in exc_info.value.detail

    def test_auth_enabled_invalid_key_raises_401(self):
        """When auth enabled, invalid key should raise 401."""
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = "valid-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key="wrong-key")

            assert exc_info.value.status_code == 401
            assert "Invalid API key" in exc_info.value.detail

    def test_timing_safe_comparison_used(self):
        """Verify timing-safe comparison is used to prevent timing attacks."""
        test_key = "test-key-123"
        with patch("src.core.security.config") as mock_config:
            mock_config.auth_enabled = True
            mock_config.api_key = test_key

            with patch("src.core.security.secrets.compare_digest") as mock_compare:
                mock_compare.return_value = True

                verify_api_key(api_key=test_key)

                mock_compare.assert_called_once_with(test_key, test_key)


class TestApiKeyHeader:
    """Tests for API key header configuration."""

    def test_header_name_is_x_api_key(self):
        """API key should be extracted from X-API-Key header."""
        assert api_key_header.model.name == "X-API-Key"

    def test_header_auto_error_is_false(self):
        """auto_error should be False to allow optional auth."""
        # APIKeyHeader stores auto_error on the instance, not the model
        assert api_key_header.auto_error is False
