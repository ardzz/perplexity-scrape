"""
MCP Authentication Middleware.

Provides API key authentication for MCP HTTP transport.
"""

import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import config


class MCPAuthMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware for API key authentication on MCP HTTP endpoints.

    When auth is enabled (API_KEY env var set):
    - Requires X-API-Key header on all requests
    - Uses timing-safe comparison to prevent timing attacks
    - Returns 401 JSON-RPC error for unauthorized requests

    When auth is disabled (API_KEY empty):
    - Allows all requests through
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and check authentication."""
        # Skip auth if disabled
        if not config.auth_enabled:
            return await call_next(request)

        # Check X-API-Key header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32001,
                        "message": "Unauthorized: Missing API key. Provide X-API-Key header.",
                    },
                    "id": None,
                },
                status_code=401,
            )

        # Timing-safe comparison to prevent timing attacks
        if not secrets.compare_digest(api_key, config.api_key):
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32001,
                        "message": "Unauthorized: Invalid API key.",
                    },
                    "id": None,
                },
                status_code=401,
            )

        return await call_next(request)
