"""
OpenAI response stream formatter.

Formats Perplexity responses into OpenAI-compatible response formats.
"""

import json
import time
import uuid
from typing import Optional

from src.models.openai_models import (
    ChatCompletionResponse,
    ChatCompletionChunk,
    Choice,
    ChoiceMessage,
    ChunkChoice,
    DeltaContent,
    UsageInfo,
)


def generate_completion_id() -> str:
    """Generate a unique completion ID in OpenAI format."""
    return f"chatcmpl-{uuid.uuid4().hex[:24]}"


def format_openai_response(
    content: str,
    model: str,
    completion_id: Optional[str] = None,
    created: Optional[int] = None,
) -> ChatCompletionResponse:
    """
    Format a complete response in OpenAI format.

    Args:
        content: The response content text
        model: The model name to include in response
        completion_id: Optional pre-generated completion ID
        created: Optional pre-generated timestamp

    Returns:
        ChatCompletionResponse ready for JSON serialization.
    """
    return ChatCompletionResponse(
        id=completion_id or generate_completion_id(),
        created=created or int(time.time()),
        model=model,
        choices=[
            Choice(
                index=0,
                message=ChoiceMessage(
                    role="assistant",
                    content=content,
                ),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(
            prompt_tokens=0,  # Perplexity doesn't provide token counts
            completion_tokens=0,
            total_tokens=0,
        ),
    )


from typing import Literal

FinishReason = Literal["stop", "length", "content_filter"]


def format_openai_chunk(
    completion_id: str,
    created: int,
    model: str,
    content: Optional[str] = None,
    role: Optional[Literal["assistant"]] = None,
    finish_reason: Optional[FinishReason] = None,
) -> ChatCompletionChunk:
    """
    Format a streaming chunk in OpenAI format.

    Args:
        completion_id: The shared completion ID for all chunks
        created: The shared creation timestamp
        model: The model name
        content: Optional content delta
        role: Optional role (sent in first chunk)
        finish_reason: Optional finish reason (sent in final chunk)

    Returns:
        ChatCompletionChunk ready for JSON serialization.
    """
    delta = DeltaContent(role=role, content=content)

    return ChatCompletionChunk(
        id=completion_id,
        created=created,
        model=model,
        choices=[
            ChunkChoice(
                index=0,
                delta=delta,
                finish_reason=finish_reason,
            )
        ],
    )


def format_sse_event(chunk: ChatCompletionChunk) -> str:
    """
    Format a chunk as an SSE data event.

    Args:
        chunk: The ChatCompletionChunk to format

    Returns:
        SSE-formatted string: "data: {json}\n\n"
    """
    return f"data: {chunk.model_dump_json()}\n\n"


def format_sse_done() -> str:
    """
    Format the final SSE done event.

    Returns:
        SSE done marker: "data: [DONE]\n\n"
    """
    return "data: [DONE]\n\n"


class StreamFormatter:
    """
    Stateful formatter for streaming responses.

    Tracks whether the role chunk has been sent and formats
    the complete streaming sequence.
    """

    def __init__(self, model: str):
        """
        Initialize the stream formatter.

        Args:
            model: The model name to include in chunks
        """
        self.model = model
        self.completion_id = generate_completion_id()
        self.created = int(time.time())
        self.has_sent_role = False

    def format_role_chunk(self) -> str:
        """
        Format and return the initial role announcement chunk.

        Returns:
            SSE-formatted role chunk, or empty string if already sent.
        """
        if self.has_sent_role:
            return ""

        self.has_sent_role = True
        chunk = format_openai_chunk(
            completion_id=self.completion_id,
            created=self.created,
            model=self.model,
            role="assistant",
        )
        return format_sse_event(chunk)

    def format_content_chunk(self, content: str) -> str:
        """
        Format a content chunk.

        Args:
            content: The text content to send

        Returns:
            SSE-formatted content chunk.
        """
        # Ensure role is sent first
        prefix = ""
        if not self.has_sent_role:
            prefix = self.format_role_chunk()

        chunk = format_openai_chunk(
            completion_id=self.completion_id,
            created=self.created,
            model=self.model,
            content=content,
        )
        return prefix + format_sse_event(chunk)

    def format_final_chunk(self) -> str:
        """
        Format the final chunk with finish_reason and DONE marker.

        Returns:
            SSE-formatted final chunk and DONE marker.
        """
        chunk = format_openai_chunk(
            completion_id=self.completion_id,
            created=self.created,
            model=self.model,
            finish_reason="stop",
        )
        return format_sse_event(chunk) + format_sse_done()
