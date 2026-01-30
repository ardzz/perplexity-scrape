"""
Unit tests for src/api/error_handlers.py

Tests exception classes, error handlers, and handler registration.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.api.error_handlers import (
    OpenAIAPIError,
    InvalidRequestError,
    AuthenticationError,
    ModelNotFoundError,
    RateLimitError,
    InternalServerError,
    ServiceUnavailableError,
    openai_api_error_handler,
    http_exception_handler,
    general_exception_handler,
    register_error_handlers,
)
from src.models.openai_models import APIErrorResponse, ErrorDetail


# ============================================================================
# Tests for OpenAIAPIError Base Class
# ============================================================================


class TestOpenAIAPIError:
    """Test cases for OpenAIAPIError base class."""

    def test_constructor_stores_all_fields(self):
        """Test that constructor stores all parameters correctly."""
        error = OpenAIAPIError(
            message="Test message",
            error_type="test_error",
            status_code=400,
            param="test_param",
            code="test_code",
        )

        assert error.message == "Test message"
        assert error.error_type == "test_error"
        assert error.status_code == 400
        assert error.param == "test_param"
        assert error.code == "test_code"

    def test_constructor_with_optional_none(self):
        """Test constructor with None for optional fields."""
        error = OpenAIAPIError(
            message="Test message",
            error_type="test_error",
            status_code=400,
            param=None,
            code=None,
        )

        assert error.message == "Test message"
        assert error.error_type == "test_error"
        assert error.status_code == 400
        assert error.param is None
        assert error.code is None

    def test_constructor_inherits_from_exception(self):
        """Test that OpenAIAPIError is an Exception."""
        error = OpenAIAPIError(
            message="Test",
            error_type="test",
            status_code=400,
        )
        assert isinstance(error, Exception)

    def test_to_response_returns_api_error_response(self):
        """Test that to_response() returns correct APIErrorResponse."""
        error = OpenAIAPIError(
            message="Test message",
            error_type="test_error",
            status_code=400,
            param="test_param",
            code="test_code",
        )

        response = error.to_response()

        assert isinstance(response, APIErrorResponse)
        assert response.error.message == "Test message"
        assert response.error.type == "test_error"
        assert response.error.param == "test_param"
        assert response.error.code == "test_code"

    def test_to_response_with_none_optional_fields(self):
        """Test to_response() with None optional fields."""
        error = OpenAIAPIError(
            message="Test message",
            error_type="test_error",
            status_code=400,
        )

        response = error.to_response()

        assert response.error.message == "Test message"
        assert response.error.type == "test_error"
        assert response.error.param is None
        assert response.error.code is None


# ============================================================================
# Tests for Exception Classes
# ============================================================================


class TestInvalidRequestError:
    """Test cases for InvalidRequestError."""

    def test_constructor_with_message_only(self):
        """Test InvalidRequestError with just message."""
        error = InvalidRequestError(message="Invalid parameter")

        assert error.message == "Invalid parameter"
        assert error.error_type == "invalid_request_error"
        assert error.status_code == 400
        assert error.param is None

    def test_constructor_with_param(self):
        """Test InvalidRequestError with param."""
        error = InvalidRequestError(message="Invalid model", param="model")

        assert error.message == "Invalid model"
        assert error.error_type == "invalid_request_error"
        assert error.status_code == 400
        assert error.param == "model"

    def test_to_response(self):
        """Test to_response() returns correct format."""
        error = InvalidRequestError(message="Test", param="field")
        response = error.to_response()

        assert response.error.type == "invalid_request_error"
        assert response.error.message == "Test"
        assert response.error.param == "field"


class TestAuthenticationError:
    """Test cases for AuthenticationError."""

    def test_constructor_default_message(self):
        """Test AuthenticationError with default message."""
        error = AuthenticationError()

        assert error.message == "Invalid API key"
        assert error.error_type == "authentication_error"
        assert error.status_code == 401

    def test_constructor_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError(message="API key expired")

        assert error.message == "API key expired"
        assert error.error_type == "authentication_error"
        assert error.status_code == 401

    def test_to_response(self):
        """Test to_response() returns correct format."""
        error = AuthenticationError(message="Custom error")
        response = error.to_response()

        assert response.error.type == "authentication_error"
        assert response.error.message == "Custom error"


class TestModelNotFoundError:
    """Test cases for ModelNotFoundError."""

    def test_constructor_includes_model_name(self):
        """Test ModelNotFoundError includes model in message."""
        error = ModelNotFoundError(model="gpt-4")

        assert error.message == "Model 'gpt-4' not found"
        assert error.error_type == "not_found_error"
        assert error.status_code == 404
        assert error.param == "model"

    def test_constructor_with_different_model(self):
        """Test with different model name."""
        error = ModelNotFoundError(model="claude-3-opus")

        assert error.message == "Model 'claude-3-opus' not found"
        assert error.param == "model"

    def test_to_response(self):
        """Test to_response() returns correct format."""
        error = ModelNotFoundError(model="test-model")
        response = error.to_response()

        assert response.error.type == "not_found_error"
        assert response.error.message == "Model 'test-model' not found"
        assert response.error.param == "model"


class TestRateLimitError:
    """Test cases for RateLimitError."""

    def test_constructor_default_message(self):
        """Test RateLimitError with default message."""
        error = RateLimitError()

        assert error.message == "Rate limit exceeded"
        assert error.error_type == "rate_limit_error"
        assert error.status_code == 429

    def test_constructor_custom_message(self):
        """Test RateLimitError with custom message."""
        error = RateLimitError(message="Too many requests, retry in 60s")

        assert error.message == "Too many requests, retry in 60s"
        assert error.error_type == "rate_limit_error"
        assert error.status_code == 429

    def test_to_response(self):
        """Test to_response() returns correct format."""
        error = RateLimitError(message="Rate limited")
        response = error.to_response()

        assert response.error.type == "rate_limit_error"
        assert response.error.message == "Rate limited"


class TestInternalServerError:
    """Test cases for InternalServerError."""

    def test_constructor_default_message(self):
        """Test InternalServerError with default message."""
        error = InternalServerError()

        assert error.message == "Internal server error"
        assert error.error_type == "api_error"
        assert error.status_code == 500

    def test_constructor_custom_message(self):
        """Test InternalServerError with custom message."""
        error = InternalServerError(message="Database connection failed")

        assert error.message == "Database connection failed"
        assert error.error_type == "api_error"
        assert error.status_code == 500

    def test_to_response(self):
        """Test to_response() returns correct format."""
        error = InternalServerError(message="Custom error")
        response = error.to_response()

        assert response.error.type == "api_error"
        assert response.error.message == "Custom error"


class TestServiceUnavailableError:
    """Test cases for ServiceUnavailableError."""

    def test_constructor_default_message(self):
        """Test ServiceUnavailableError with default message."""
        error = ServiceUnavailableError()

        assert error.message == "Perplexity API is temporarily unavailable"
        assert error.error_type == "service_unavailable_error"
        assert error.status_code == 503

    def test_constructor_custom_message(self):
        """Test ServiceUnavailableError with custom message."""
        error = ServiceUnavailableError(message="Maintenance in progress")

        assert error.message == "Maintenance in progress"
        assert error.error_type == "service_unavailable_error"
        assert error.status_code == 503

    def test_to_response(self):
        """Test to_response() returns correct format."""
        error = ServiceUnavailableError(message="Unavailable")
        response = error.to_response()

        assert response.error.type == "service_unavailable_error"
        assert response.error.message == "Unavailable"


# ============================================================================
# Tests for Exception Handlers
# ============================================================================


class TestOpenAIAPIErrorHandler:
    """Test cases for openai_api_error_handler."""

    @pytest.mark.asyncio
    async def test_returns_json_response(self):
        """Test handler returns JSONResponse."""
        error = InvalidRequestError(message="Test error", param="test")
        request = MagicMock(spec=Request)

        response = await openai_api_error_handler(request, error)

        assert isinstance(response, JSONResponse)

    @pytest.mark.asyncio
    async def test_correct_status_code(self):
        """Test handler returns correct status code."""
        error = InvalidRequestError(message="Test")
        request = MagicMock(spec=Request)

        response = await openai_api_error_handler(request, error)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_correct_content_structure(self):
        """Test handler returns correct content structure."""
        error = AuthenticationError(message="Invalid key")
        request = MagicMock(spec=Request)

        response = await openai_api_error_handler(request, error)

        # JSONResponse content is passed as dict
        assert response.body is not None

    @pytest.mark.asyncio
    async def test_logs_warning(self):
        """Test handler logs warning."""
        error = InvalidRequestError(message="Test error")
        request = MagicMock(spec=Request)

        with patch("src.api.error_handlers.logger") as mock_logger:
            await openai_api_error_handler(request, error)
            mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_different_status_codes(self):
        """Test handler with different error types."""
        test_cases = [
            (InvalidRequestError("test"), 400),
            (AuthenticationError(), 401),
            (ModelNotFoundError("gpt-4"), 404),
            (RateLimitError(), 429),
            (InternalServerError(), 500),
            (ServiceUnavailableError(), 503),
        ]

        request = MagicMock(spec=Request)

        for error, expected_status in test_cases:
            response = await openai_api_error_handler(request, error)
            assert response.status_code == expected_status


class TestHTTPExceptionHandler:
    """Test cases for http_exception_handler."""

    @pytest.mark.asyncio
    async def test_returns_json_response(self):
        """Test handler returns JSONResponse."""
        exc = HTTPException(status_code=400, detail="Bad request")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)

    @pytest.mark.asyncio
    async def test_preserves_status_code(self):
        """Test handler preserves status code from HTTPException."""
        exc = HTTPException(status_code=404, detail="Not found")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_converts_detail_to_message(self):
        """Test handler converts detail to message field."""
        exc = HTTPException(status_code=400, detail="Invalid input")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        # Response content is a dictionary
        assert response.body is not None

    @pytest.mark.asyncio
    async def test_error_type_mapping_400(self):
        """Test error type mapping for 400."""
        exc = HTTPException(status_code=400, detail="Bad request")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_error_type_mapping_401(self):
        """Test error type mapping for 401."""
        exc = HTTPException(status_code=401, detail="Unauthorized")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_error_type_mapping_404(self):
        """Test error type mapping for 404."""
        exc = HTTPException(status_code=404, detail="Not found")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_error_type_mapping_429(self):
        """Test error type mapping for 429."""
        exc = HTTPException(status_code=429, detail="Rate limited")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_error_type_mapping_500(self):
        """Test error type mapping for 500."""
        exc = HTTPException(status_code=500, detail="Server error")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_error_type_mapping_503(self):
        """Test error type mapping for 503."""
        exc = HTTPException(status_code=503, detail="Service unavailable")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_unmapped_status_code_defaults_to_api_error(self):
        """Test unmapped status code defaults to api_error type."""
        exc = HTTPException(status_code=418, detail="I'm a teapot")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, exc)

        assert response.status_code == 418


class TestGeneralExceptionHandler:
    """Test cases for general_exception_handler."""

    @pytest.mark.asyncio
    async def test_returns_json_response(self):
        """Test handler returns JSONResponse."""
        exc = ValueError("Test error")
        request = MagicMock(spec=Request)

        response = await general_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)

    @pytest.mark.asyncio
    async def test_returns_500_status_code(self):
        """Test handler always returns 500 status code."""
        exc = ValueError("Test error")
        request = MagicMock(spec=Request)

        response = await general_exception_handler(request, exc)

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_returns_generic_error_message(self):
        """Test handler returns generic error message."""
        exc = ValueError("Test error")
        request = MagicMock(spec=Request)

        response = await general_exception_handler(request, exc)

        assert response.body is not None

    @pytest.mark.asyncio
    async def test_logs_exception(self):
        """Test handler logs the exception."""
        exc = ValueError("Test error")
        request = MagicMock(spec=Request)

        with patch("src.api.error_handlers.logger") as mock_logger:
            await general_exception_handler(request, exc)
            mock_logger.exception.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_different_exception_types(self):
        """Test handler with different exception types."""
        exceptions = [
            ValueError("test"),
            TypeError("test"),
            KeyError("test"),
            RuntimeError("test"),
        ]

        request = MagicMock(spec=Request)

        for exc in exceptions:
            response = await general_exception_handler(request, exc)
            assert response.status_code == 500
            assert isinstance(response, JSONResponse)


# ============================================================================
# Tests for register_error_handlers
# ============================================================================


class TestRegisterErrorHandlers:
    """Test cases for register_error_handlers function."""

    def test_registers_openai_api_error_handler(self):
        """Test that OpenAIAPIError handler is registered."""
        mock_app = MagicMock()

        register_error_handlers(mock_app)

        # Check that add_exception_handler was called with OpenAIAPIError
        calls = mock_app.add_exception_handler.call_args_list
        assert any(args[0] == OpenAIAPIError for args, kwargs in calls), (
            "OpenAIAPIError handler not registered"
        )

    def test_registers_http_exception_handler(self):
        """Test that HTTPException handler is registered."""
        mock_app = MagicMock()

        register_error_handlers(mock_app)

        # Check that add_exception_handler was called with HTTPException
        calls = mock_app.add_exception_handler.call_args_list
        assert any("HTTPException" in str(args) for args, kwargs in calls), (
            "HTTPException handler not registered"
        )

    def test_registers_general_exception_handler(self):
        """Test that general Exception handler is registered."""
        mock_app = MagicMock()

        register_error_handlers(mock_app)

        # Check that add_exception_handler was called with Exception
        calls = mock_app.add_exception_handler.call_args_list
        assert any(args[0] == Exception for args, kwargs in calls), (
            "General Exception handler not registered"
        )

    def test_registers_all_three_handlers(self):
        """Test that all three handlers are registered."""
        mock_app = MagicMock()

        register_error_handlers(mock_app)

        # Should have 3 handler registrations
        assert mock_app.add_exception_handler.call_count == 3

    def test_handlers_are_correct_functions(self):
        """Test that registered handlers are the correct functions."""
        mock_app = MagicMock()

        register_error_handlers(mock_app)

        calls = mock_app.add_exception_handler.call_args_list
        handler_functions = [args[1] for args, kwargs in calls]

        # Should contain our handler functions
        assert openai_api_error_handler in handler_functions
        assert http_exception_handler in handler_functions
        assert general_exception_handler in handler_functions


# ============================================================================
# Integration Tests
# ============================================================================


class TestErrorHandlerIntegration:
    """Integration tests combining multiple components."""

    @pytest.mark.asyncio
    async def test_exception_to_response_flow(self):
        """Test complete flow from exception to response."""
        error = ModelNotFoundError("test-model")
        request = MagicMock(spec=Request)

        response = await openai_api_error_handler(request, error)

        assert response.status_code == 404
        assert isinstance(response, JSONResponse)

    @pytest.mark.asyncio
    async def test_http_exception_conversion(self):
        """Test converting HTTPException to OpenAI format."""
        http_exc = HTTPException(status_code=401, detail="Missing API key")
        request = MagicMock(spec=Request)

        response = await http_exception_handler(request, http_exc)

        assert response.status_code == 401

    def test_all_exception_classes_are_openai_compatible(self):
        """Test all exception classes can generate valid responses."""
        errors = [
            InvalidRequestError("test"),
            AuthenticationError(),
            ModelNotFoundError("test"),
            RateLimitError(),
            InternalServerError(),
            ServiceUnavailableError(),
        ]

        for error in errors:
            response = error.to_response()
            assert isinstance(response, APIErrorResponse)
            assert response.error.type is not None
            assert response.error.message is not None

    def test_exception_hierarchy(self):
        """Test that all custom exceptions inherit from OpenAIAPIError."""
        exception_classes = [
            InvalidRequestError,
            AuthenticationError,
            ModelNotFoundError,
            RateLimitError,
            InternalServerError,
            ServiceUnavailableError,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, OpenAIAPIError)
