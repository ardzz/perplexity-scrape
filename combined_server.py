"""
Combined FastAPI + MCP Server Entry Point.

Serves both:
- OpenAI-compatible REST API at /v1/...
- MCP streamable-http at /mcp

Run with: python combined_server.py

Example usage:
    # REST API
    curl http://localhost:8045/v1/models

    # MCP (initialize session first, then call tools)
    curl -X POST http://localhost:8045/mcp \
      -H "Content-Type: application/json" \
      -H "Accept: application/json, text/event-stream" \
      -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from src.config import config
from src.api.routes import router
from src.api.error_handlers import register_error_handlers
from src.core.mcp_auth import MCPAuthMiddleware

# Import the MCP server instance from server.py
from server import mcp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    """Combined lifespan for FastAPI + MCP."""
    logger.info(f"Starting {config.api_title} v{config.api_version}")
    logger.info(
        f"Server running at http://{config.rest_api_host}:{config.rest_api_port}"
    )
    logger.info("REST API: /v1/chat/completions, /v1/models")
    logger.info("MCP HTTP: /mcp (streamable-http transport)")
    logger.info("Documentation: /docs")

    # Start MCP session manager (required for streamable-http transport)
    async with mcp.session_manager.run():
        yield

    logger.info("Shutting down...")


# Get the MCP Starlette app to extract its route endpoint
# We set path="/" so the route is created at "/" internally
mcp.settings.streamable_http_path = "/"
mcp_starlette_app = mcp.streamable_http_app()

# Extract the StreamableHTTPASGIApp endpoint from the MCP route
mcp_route = mcp_starlette_app.routes[0]  # The route at "/"
mcp_asgi_endpoint = mcp_route.endpoint  # StreamableHTTPASGIApp instance


class MCPWithAuth:
    """Wrapper that adds authentication middleware to the MCP ASGI endpoint."""

    def __init__(self, app: ASGIApp):
        self.app = app
        self.auth_middleware = MCPAuthMiddleware(app)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Apply auth middleware, which will call self.app if auth passes
        await self.auth_middleware(scope, receive, send)


# Create the authenticated MCP endpoint
mcp_endpoint_with_auth = MCPWithAuth(mcp_asgi_endpoint)


# Create FastAPI app with combined lifespan
app = FastAPI(
    title=config.api_title,
    version=config.api_version,
    description="OpenAI-compatible REST API + MCP Server for Perplexity AI",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=combined_lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
register_error_handlers(app)

# Include REST API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "name": config.api_title,
        "version": config.api_version,
        "status": "running",
        "endpoints": {
            "rest_api": {
                "chat_completions": "/v1/chat/completions",
                "models": "/v1/models",
                "health": "/health",
            },
            "mcp": {
                "endpoint": "/mcp",
                "transport": "streamable-http",
                "methods": ["tools/list", "tools/call"],
            },
            "docs": "/docs",
        },
    }


# Add MCP routes directly to FastAPI's router
# We add BOTH /mcp and /mcp/ to handle requests with or without trailing slash
# This prevents the 307 redirect that would otherwise occur
# The Route with no methods= accepts all HTTP methods (GET, POST, DELETE)
app.routes.append(Route("/mcp", endpoint=mcp_endpoint_with_auth))
app.routes.append(Route("/mcp/", endpoint=mcp_endpoint_with_auth))


if __name__ == "__main__":
    uvicorn.run(
        "combined_server:app",
        host=config.rest_api_host,
        port=config.rest_api_port,
        reload=True,
    )
