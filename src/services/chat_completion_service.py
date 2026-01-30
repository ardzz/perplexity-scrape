"""
Chat completion service.

High-level service that orchestrates chat completion requests.
"""

import logging
from typing import Generator, Union

from fastapi.responses import StreamingResponse

from perplexity_client import PerplexityClient
from src.models.openai_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from src.services.perplexity_adapter import PerplexityAdapter
from src.services.stream_formatter import (
    StreamFormatter,
    format_openai_response,
)

logger = logging.getLogger(__name__)


class ChatCompletionService:
    """
    Service for handling OpenAI-compatible chat completion requests.

    Orchestrates the flow from request validation through response formatting.
    """

    def __init__(self, client: PerplexityClient):
        """
        Initialize the chat completion service.

        Args:
            client: The PerplexityClient instance
        """
        self._adapter = PerplexityAdapter(client)

    def handle_completion(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        """
        Handle a non-streaming chat completion request.

        Args:
            request: The validated ChatCompletionRequest

        Returns:
            ChatCompletionResponse with the completion.
        """
        logger.info(f"Processing completion request for model: {request.model}")

        # Execute completion
        response_text, model_name = self._adapter.complete(
            messages=request.messages,
            model=request.model,
        )

        # Format as OpenAI response
        return format_openai_response(
            content=response_text,
            model=model_name,
        )

    def handle_streaming(
        self,
        request: ChatCompletionRequest,
    ) -> StreamingResponse:
        """
        Handle a streaming chat completion request.

        Args:
            request: The validated ChatCompletionRequest

        Returns:
            StreamingResponse with SSE-formatted chunks.
        """
        logger.info(f"Processing streaming request for model: {request.model}")

        # Get the stream generator
        chunk_generator, model_name = self._adapter.stream(
            messages=request.messages,
            model=request.model,
        )

        # Create a streaming response generator
        def generate_sse():
            """Generate SSE-formatted chunks."""
            formatter = StreamFormatter(model=model_name)

            # Send initial role chunk
            yield formatter.format_role_chunk()

            # Stream content chunks
            for text_chunk in chunk_generator:
                if text_chunk:
                    yield formatter.format_content_chunk(text_chunk)

            # Send final chunk
            yield formatter.format_final_chunk()

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    def handle_request(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse | StreamingResponse:
        """
        Handle a chat completion request (streaming or non-streaming).

        Args:
            request: The validated ChatCompletionRequest

        Returns:
            ChatCompletionResponse or StreamingResponse based on request.stream
        """
        if request.stream:
            return self.handle_streaming(request)
        return self.handle_completion(request)
