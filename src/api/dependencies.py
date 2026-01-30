"""
FastAPI dependency injection.

Provides shared dependencies for API routes.
"""

import logging
from typing import Optional

from fastapi import Depends, Header

from perplexity_client import PerplexityClient

logger = logging.getLogger(__name__)


# ============================================================================
# Singleton Instances
# ============================================================================

# Lazily initialized Perplexity client
_perplexity_client: Optional[PerplexityClient] = None


def get_perplexity_client() -> PerplexityClient:
    """
    Get or create the Perplexity client singleton.

    Returns:
        The shared PerplexityClient instance.

    Raises:
        ValueError: If required environment variables are not set.
    """
    global _perplexity_client
    if _perplexity_client is None:
        _perplexity_client = PerplexityClient()
    return _perplexity_client


# ============================================================================
# FastAPI Dependencies
# ============================================================================


def get_client() -> PerplexityClient:
    """
    FastAPI dependency for PerplexityClient.

    Usage:
        @app.post("/v1/chat/completions")
        async def chat_completions(
            client: PerplexityClient = Depends(get_client)
        ):
            ...
    """
    return get_perplexity_client()


def get_api_key(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[str]:
    """
    Extract API key from Authorization header.

    The OpenAI format uses "Bearer <key>" format.
    Currently this is a placeholder - no validation is performed.

    Args:
        authorization: The Authorization header value

    Returns:
        The extracted API key, or None if not provided.
    """
    if not authorization:
        return None

    # Extract token from "Bearer <token>" format
    if authorization.startswith("Bearer "):
        return authorization[7:]

    return authorization


# ============================================================================
# Type Aliases for Dependency Injection
# ============================================================================

# Usage: client: ClientDep = Depends(get_client)
ClientDep = PerplexityClient
