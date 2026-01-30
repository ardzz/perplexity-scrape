"""
API Key authentication middleware.

Provides API key validation for protecting REST endpoints.
"""

import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.config import config

# API key header extractor - auto_error=False to allow optional auth
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key_header() -> APIKeyHeader:
    """Get the API key header security scheme."""
    return api_key_header


def verify_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """
    Verify the API key from request header.

    When auth is enabled (API_KEY is set in env):
    - Missing key → 401 Unauthorized
    - Invalid key → 401 Unauthorized
    - Valid key → Returns the key

    When auth is disabled (API_KEY is empty):
    - Always passes, returns None

    Uses timing-safe comparison to prevent timing attacks.

    Args:
        api_key: The API key from X-API-Key header

    Returns:
        The validated API key, or None if auth is disabled

    Raises:
        HTTPException: 401 if auth is enabled and key is missing/invalid
    """
    # If auth is disabled, allow all requests
    if not config.auth_enabled:
        return None

    # Auth is enabled - key is required
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Timing-safe comparison to prevent timing attacks
    if not secrets.compare_digest(api_key, config.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key
