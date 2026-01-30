"""
OpenAI-compatible request and response models.

These models follow the OpenAI Chat Completions API specification
for maximum compatibility with existing clients.
"""

import time
import uuid
from enum import Enum
from typing import Optional, Literal, Union

from pydantic import BaseModel, Field


# ============================================================================
# Request Models
# ============================================================================


class MessageRole(str, Enum):
    """Valid message roles in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """A single message in the conversation."""

    role: MessageRole
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""

    model: str = Field(..., description="Model ID to use for completion")
    messages: list[ChatMessage] = Field(
        ..., min_length=1, description="Conversation messages"
    )
    stream: bool = Field(default=False, description="Enable streaming response")
    temperature: Optional[float] = Field(
        default=1.0, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None, ge=1, description="Maximum tokens in response"
    )
    top_p: Optional[float] = Field(
        default=1.0, ge=0.0, le=1.0, description="Nucleus sampling"
    )
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[Union[list[str], str]] = Field(
        default=None, description="Stop sequences"
    )
    user: Optional[str] = Field(default=None, description="User identifier")


# ============================================================================
# Response Models (Non-streaming)
# ============================================================================


class UsageInfo(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChoiceMessage(BaseModel):
    """Message in completion choice."""

    role: Literal["assistant"] = "assistant"
    content: str
    refusal: Optional[str] = None


class Choice(BaseModel):
    """A single completion choice."""

    index: int = 0
    message: ChoiceMessage
    finish_reason: Literal["stop", "length", "content_filter"] = "stop"
    logprobs: Optional[dict] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""

    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:24]}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: list[Choice]
    usage: UsageInfo = Field(default_factory=UsageInfo)
    service_tier: Optional[str] = "default"
    system_fingerprint: Optional[str] = None


# ============================================================================
# Streaming Models
# ============================================================================


class DeltaContent(BaseModel):
    """Delta content in streaming chunk."""

    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None


class ChunkChoice(BaseModel):
    """Choice in streaming chunk."""

    index: int = 0
    delta: DeltaContent
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None
    logprobs: Optional[dict] = None


class ChatCompletionChunk(BaseModel):
    """OpenAI-compatible streaming chunk."""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChunkChoice]
    usage: Optional[UsageInfo] = None


# ============================================================================
# Error Models
# ============================================================================


class ErrorDetail(BaseModel):
    """Error detail object."""

    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None


class APIErrorResponse(BaseModel):
    """OpenAI-compatible error response."""

    error: ErrorDetail


# ============================================================================
# Model Information
# ============================================================================


class ModelInfo(BaseModel):
    """Information about an available model."""

    id: str
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "perplexity"


class ModelListResponse(BaseModel):
    """Response for /v1/models endpoint."""

    object: Literal["list"] = "list"
    data: list[ModelInfo]
