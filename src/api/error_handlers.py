"""
OpenAI-compatible error handlers.

Exception classes and FastAPI exception handlers for OpenAI format errors.
"""

import logging
from typing import Optional

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.models.openai_models import APIErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Classes
# ============================================================================


class OpenAIAPIError(Exception):
    """Base exception for OpenAI-compatible API errors."""

    def __init__(
        self,
        message: str,
        error_type: str,
        status_code: int,
        param: Optional[str] = None,
        code: Optional[str] = None,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.param = param
        self.code = code
        super().__init__(message)

    def to_response(self) -> APIErrorResponse:
        """Convert to OpenAI-compatible error response."""
        return APIErrorResponse(
            error=ErrorDetail(
                message=self.message,
                type=self.error_type,
                param=self.param,
                code=self.code,
            )
        )


class InvalidRequestError(OpenAIAPIError):
    """400 Bad Request - Malformed request."""

    def __init__(self, message: str, param: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="invalid_request_error",
            status_code=400,
            param=param,
        )


class AuthenticationError(OpenAIAPIError):
    """401 Unauthorized - Invalid API key."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(
            message=message,
            error_type="authentication_error",
            status_code=401,
        )


class ModelNotFoundError(OpenAIAPIError):
    """404 Not Found - Model not found."""

    def __init__(self, model: str):
        super().__init__(
            message=f"Model '{model}' not found",
            error_type="not_found_error",
            status_code=404,
            param="model",
        )


class RateLimitError(OpenAIAPIError):
    """429 Too Many Requests - Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_type="rate_limit_error",
            status_code=429,
        )


class InternalServerError(OpenAIAPIError):
    """500 Internal Server Error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            message=message,
            error_type="api_error",
            status_code=500,
        )


class ServiceUnavailableError(OpenAIAPIError):
    """503 Service Unavailable - Perplexity API unavailable."""

    def __init__(self, message: str = "Perplexity API is temporarily unavailable"):
        super().__init__(
            message=message,
            error_type="service_unavailable_error",
            status_code=503,
        )


# ============================================================================
# Exception Handlers
# ============================================================================


async def openai_api_error_handler(
    request: Request, exc: OpenAIAPIError
) -> JSONResponse:
    """Handle OpenAI API errors."""
    logger.warning(f"API Error: {exc.error_type} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response().model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Convert FastAPI HTTPException to OpenAI format."""
    error_type_map = {
        400: "invalid_request_error",
        401: "authentication_error",
        404: "not_found_error",
        429: "rate_limit_error",
        500: "api_error",
        503: "service_unavailable_error",
    }
    error_type = error_type_map.get(exc.status_code, "api_error")

    response = APIErrorResponse(
        error=ErrorDetail(
            message=str(exc.detail),
            type=error_type,
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions in OpenAI format."""
    logger.exception(f"Unexpected error: {exc}")
    response = APIErrorResponse(
        error=ErrorDetail(
            message="Internal server error",
            type="api_error",
        )
    )
    return JSONResponse(
        status_code=500,
        content=response.model_dump(),
    )


def register_error_handlers(app):
    """Register all error handlers with the FastAPI app."""
    from fastapi import HTTPException as FastAPIHTTPException

    app.add_exception_handler(OpenAIAPIError, openai_api_error_handler)
    app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
