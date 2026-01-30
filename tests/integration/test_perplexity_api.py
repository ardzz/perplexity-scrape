"""
Integration tests for Perplexity API.

These tests make REAL API calls and require valid credentials.
They are skipped if credentials are not available.

Credentials can be provided via:
1. Local .env file (for local development)
2. Environment variables (for CI/CD - GitHub Actions secrets)

To run these tests locally:
1. Set up your .env file with valid Perplexity credentials
2. Run: pytest tests/integration/ -v

Note: These tests are rate-limited and should be run sparingly.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# This allows credentials from either .env file OR environment variables (GitHub secrets)
env_file = Path(__file__).parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file, override=False)  # Don't override existing env vars


def _has_valid_credentials() -> bool:
    """Check if valid Perplexity credentials are available."""
    token = os.getenv("PERPLEXITY_SESSION_TOKEN")
    # Skip if no token or if it's a placeholder/test value
    if not token:
        return False
    if token in ("test-token", "your_session_token_here", "your_session_token"):
        return False
    return True


# Skip all tests in this module if credentials are not available
pytestmark = pytest.mark.skipif(
    not _has_valid_credentials(),
    reason="Real Perplexity credentials not available (set via .env file or environment variables)",
)


class TestPerplexityClientIntegration:
    """Integration tests for PerplexityClient with real API."""

    @pytest.fixture
    def client(self):
        """Create a real PerplexityClient instance."""
        from src.core.perplexity_client import PerplexityClient

        return PerplexityClient()

    def test_client_initialization_with_real_credentials(self, client):
        """Test that client initializes with real credentials."""
        assert client.session_token is not None
        assert client.cf_clearance is not None
        assert client.visitor_id is not None

    def test_ask_returns_response(self, client):
        """Test that ask() returns a valid response."""
        response = client.ask(
            query="What is 2 + 2?",
            mode="copilot",
            model_preference="pplx_alpha",  # Use fast model for testing
            is_incognito=True,
        )

        assert response is not None
        assert response.text is not None
        assert len(response.text) > 0
        # The answer should contain "4" somewhere
        assert "4" in response.text

    def test_ask_stream_yields_events(self, client):
        """Test that ask_stream() yields SSE events."""
        events = list(
            client.ask_stream(
                query="Say hello",
                mode="copilot",
                model_preference="pplx_alpha",
                is_incognito=True,
            )
        )

        assert len(events) > 0
        # At least one event should have blocks
        has_blocks = any("blocks" in event for event in events)
        assert has_blocks, "Expected at least one event with blocks"

    def test_ask_with_different_models(self, client):
        """Test that different models can be used."""
        models_to_test = ["pplx_alpha", "claude45sonnetthinking"]

        for model in models_to_test:
            response = client.ask(
                query="What is Python?",
                mode="copilot",
                model_preference=model,
                is_incognito=True,
            )
            assert response.text is not None
            assert len(response.text) > 0


class TestPerplexityAdapterIntegration:
    """Integration tests for PerplexityAdapter with real API."""

    @pytest.fixture
    def adapter(self):
        """Create a real PerplexityAdapter instance."""
        from src.core.perplexity_client import PerplexityClient
        from src.services.perplexity_adapter import PerplexityAdapter

        client = PerplexityClient()
        return PerplexityAdapter(client)

    def test_complete_returns_response(self, adapter):
        """Test non-streaming completion."""
        from src.models.openai_models import ChatMessage, MessageRole

        messages = [ChatMessage(role=MessageRole.USER, content="What is 1 + 1?")]

        response_text, model_name = adapter.complete(
            messages=messages,
            model="pplx-alpha",  # Use fast model
        )

        assert response_text is not None
        assert len(response_text) > 0
        assert "2" in response_text

    def test_stream_yields_chunks(self, adapter):
        """Test streaming completion."""
        from src.models.openai_models import ChatMessage, MessageRole

        messages = [ChatMessage(role=MessageRole.USER, content="Count from 1 to 3")]

        generator, model_name = adapter.stream(
            messages=messages,
            model="pplx-alpha",
        )

        chunks = list(generator)
        assert len(chunks) > 0

        # Combine all chunks
        full_text = "".join(chunks)
        assert len(full_text) > 0


class TestChatCompletionServiceIntegration:
    """Integration tests for ChatCompletionService with real API."""

    @pytest.fixture
    def service(self):
        """Create a real ChatCompletionService instance."""
        from src.core.perplexity_client import PerplexityClient
        from src.services.chat_completion_service import ChatCompletionService

        client = PerplexityClient()
        return ChatCompletionService(client)

    def test_handle_completion_returns_openai_format(self, service):
        """Test that completion returns OpenAI-compatible response."""
        from src.models.openai_models import (
            ChatCompletionRequest,
            ChatCompletionResponse,
            ChatMessage,
            MessageRole,
        )

        request = ChatCompletionRequest(
            model="pplx-alpha",
            messages=[ChatMessage(role=MessageRole.USER, content="Say hi")],
            stream=False,
        )

        response = service.handle_completion(request)

        assert isinstance(response, ChatCompletionResponse)
        assert response.id.startswith("chatcmpl-")
        assert response.object == "chat.completion"
        assert len(response.choices) == 1
        assert response.choices[0].message.role == "assistant"
        assert len(response.choices[0].message.content) > 0

    def test_handle_streaming_returns_streaming_response(self, service):
        """Test that streaming returns StreamingResponse."""
        from fastapi.responses import StreamingResponse
        from src.models.openai_models import (
            ChatCompletionRequest,
            ChatMessage,
            MessageRole,
        )

        request = ChatCompletionRequest(
            model="pplx-alpha",
            messages=[ChatMessage(role=MessageRole.USER, content="Say hello")],
            stream=True,
        )

        response = service.handle_streaming(request)

        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/event-stream"


class TestRESTAPIIntegration:
    """Integration tests for the REST API endpoints."""

    @pytest.fixture
    async def test_client(self):
        """Create an async test client for the REST API."""
        from httpx import AsyncClient, ASGITransport
        from rest_api_service import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client):
        """Test the health endpoint."""
        response = await test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_models_endpoint(self, test_client):
        """Test the models list endpoint."""
        response = await test_client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0

    @pytest.mark.asyncio
    async def test_chat_completions_endpoint(self, test_client):
        """Test the chat completions endpoint with real API."""
        response = await test_client.post(
            "/v1/chat/completions",
            json={
                "model": "pplx-alpha",
                "messages": [{"role": "user", "content": "What is 5 + 5?"}],
                "stream": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "chat.completion"
        assert len(data["choices"]) == 1
        assert "10" in data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
