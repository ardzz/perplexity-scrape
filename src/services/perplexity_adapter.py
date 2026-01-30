"""
Perplexity adapter for OpenAI-compatible API.

Adapts Perplexity's API to the OpenAI chat completions format.
"""

import logging
from typing import Generator, Optional

from src.core.perplexity_client import PerplexityClient
from src.models.openai_models import ChatMessage, MessageRole
from src.models.model_mapping import get_model_config, ModelConfig
from src.services.chunk_extractor import ChunkExtractor
from src.models.perplexity_models import StreamingState

logger = logging.getLogger(__name__)


class PerplexityAdapter:
    """
    Adapter that wraps PerplexityClient for OpenAI-compatible operations.

    All operations use is_incognito=True to ensure REST API requests
    don't appear in the user's Perplexity dashboard.
    """

    def __init__(self, client: PerplexityClient):
        """
        Initialize the adapter.

        Args:
            client: The PerplexityClient instance to wrap
        """
        self._client = client

    def format_messages_as_query(self, messages: list[ChatMessage]) -> str:
        """
        Convert OpenAI-style messages to a Perplexity query string.

        Perplexity expects a single query string rather than a conversation.
        This method formats the conversation into a coherent query.

        Args:
            messages: List of ChatMessage objects from the request

        Returns:
            A formatted query string for Perplexity.
        """
        # Extract system message if present
        system_message = None
        conversation = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                role_prefix = "User" if msg.role == MessageRole.USER else "Assistant"
                conversation.append(f"{role_prefix}: {msg.content}")

        # Build the query
        parts = []

        # Add system context if present
        if system_message:
            parts.append(f"[Context: {system_message}]")

        # For single user message, just use the content directly
        if len(messages) == 1 and messages[0].role == MessageRole.USER:
            return messages[0].content

        # For multi-turn conversations, format as dialogue
        if conversation:
            parts.append("\n".join(conversation))

        return "\n\n".join(parts) if parts else ""

    def complete(
        self,
        messages: list[ChatMessage],
        model: str,
    ) -> tuple[str, str]:
        """
        Execute a non-streaming completion.

        Args:
            messages: The conversation messages
            model: The OpenAI-style model name

        Returns:
            Tuple of (response_text, perplexity_model_name)
        """
        # Get model configuration
        config = get_model_config(model)

        # Format messages as query
        query = self.format_messages_as_query(messages)

        logger.debug(f"Executing completion with model {config.perplexity_model}")

        # Call Perplexity (always incognito for REST API)
        response = self._client.ask(
            query=query,
            mode=config.mode,
            model_preference=config.perplexity_model,
            search_focus=config.search_focus,
            sources=config.sources,
            is_incognito=True,  # MANDATORY for REST API
        )

        return response.text, config.perplexity_model

    def stream(
        self,
        messages: list[ChatMessage],
        model: str,
    ) -> tuple[Generator[str, None, None], str]:
        """
        Execute a streaming completion.

        This method returns a generator that yields text chunks
        extracted from Perplexity's SSE stream.

        Args:
            messages: The conversation messages
            model: The OpenAI-style model name

        Returns:
            Tuple of (generator of text chunks, perplexity_model_name)
        """
        # Get model configuration
        config = get_model_config(model)

        # Format messages as query
        query = self.format_messages_as_query(messages)

        logger.debug(f"Starting stream with model {config.perplexity_model}")

        # Create a generator wrapper
        def chunk_generator():
            """Synchronous generator that yields text chunks."""
            extractor = ChunkExtractor()

            for event_data in self._client.ask_stream(
                query=query,
                mode=config.mode,
                model_preference=config.perplexity_model,
                search_focus=config.search_focus,
                sources=config.sources,
                is_incognito=True,  # MANDATORY for REST API
            ):
                for chunk in extractor.process_event(event_data):
                    if chunk:
                        yield chunk

        return chunk_generator(), config.perplexity_model
