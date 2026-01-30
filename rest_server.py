"""
FastAPI REST Server Entry Point.

Provides OpenAI-compatible /v1/chat/completions endpoint for Perplexity AI.
Run with: python rest_server.py
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import config
from src.api.routes import router
from src.api.error_handlers import register_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.api_title,
    version=config.api_version,
    description="OpenAI-compatible REST API for Perplexity AI",
    docs_url="/docs",
    redoc_url="/redoc",
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

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": config.api_title,
        "version": config.api_version,
        "status": "running",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info(f"Starting {config.api_title} v{config.api_version}")
    logger.info(
        f"Server running at http://{config.rest_api_host}:{config.rest_api_port}"
    )
    logger.info("Documentation available at /docs")


if __name__ == "__main__":
    uvicorn.run(
        "rest_server:app",
        host=config.rest_api_host,
        port=config.rest_api_port,
        reload=True,
    )
