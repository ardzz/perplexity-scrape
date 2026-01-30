"""
FastAPI dependency injection.

Provides shared dependencies for API routes.
"""

import logging
from typing import Optional

from fastapi import Depends

from src.core.perplexity_client import PerplexityClient
from src.core.security import verify_api_key

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


# Re-export verify_api_key as get_api_key for backward compatibility
get_api_key = verify_api_key


# ============================================================================
# Type Aliases for Dependency Injection
# ============================================================================

# Usage: client: ClientDep = Depends(get_client)
ClientDep = PerplexityClient
