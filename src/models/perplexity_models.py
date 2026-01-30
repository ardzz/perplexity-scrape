"""
Perplexity SSE response models.

Internal models for parsing Perplexity's complex SSE format.
NOT exposed to API consumers - only used for internal processing.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Any, Literal

from pydantic import BaseModel


# ============================================================================
# SSE Event Models
# ============================================================================


class JSONPatch(BaseModel):
    """Single JSON Patch operation (RFC 6902)."""

    op: Literal["add", "replace", "remove"]
    path: str
    value: Optional[Any] = None


class DiffBlock(BaseModel):
    """Diff block with JSON Patch operations."""

    field: str  # e.g., "markdown_block"
    patches: list[JSONPatch] = []


class MarkdownBlock(BaseModel):
    """Markdown block containing answer text."""

    progress: Literal["IN_PROGRESS", "DONE"] = "IN_PROGRESS"
    chunks: list[str] = []
    chunk_starting_offset: int = 0
    answer: Optional[str] = None
    media_items: Optional[list[Any]] = None
    inline_token_annotations: list[Any] = []


class PerplexityBlock(BaseModel):
    """A content block in Perplexity SSE."""

    intended_usage: str
    diff_block: Optional[DiffBlock] = None
    plan_block: Optional[dict[str, Any]] = None
    markdown_block: Optional[MarkdownBlock] = None


class PerplexitySSEEvent(BaseModel):
    """Top-level SSE event from Perplexity."""

    backend_uuid: str = ""
    uuid: str = ""
    display_model: str = ""
    mode: str = ""
    search_focus: str = ""
    text_completed: bool = False
    message_mode: str = "STREAMING"
    blocks: list[PerplexityBlock] = []
    thread_url_slug: Optional[str] = None


# ============================================================================
# Aggregation State Models
# ============================================================================


@dataclass
class ChunkAggregator:
    """
    Aggregates text chunks from Perplexity SSE stream.

    Applies JSON Patch operations to build up the response
    incrementally as chunks arrive.
    """

    chunks: list[str] = field(default_factory=list)
    is_complete: bool = False

    def apply_patch(self, patch: JSONPatch) -> Optional[str]:
        """
        Apply a JSON Patch and return new text if any.

        Args:
            patch: The JSON Patch operation to apply

        Returns:
            New chunk text if patch adds content, None otherwise.
        """
        if patch.op == "add" and "/chunks/" in patch.path:
            # Adding a new chunk - extract and store
            chunk_text = str(patch.value) if patch.value is not None else ""
            self.chunks.append(chunk_text)
            return chunk_text
        elif patch.op == "replace":
            if patch.path == "/progress" and patch.value == "DONE":
                self.is_complete = True
            elif patch.path == "" and isinstance(patch.value, dict):
                # Initial block setup - extract initial chunks
                initial_chunks = patch.value.get("chunks", [])
                for chunk in initial_chunks:
                    self.chunks.append(str(chunk))
                return "".join(initial_chunks) if initial_chunks else None
        return None

    def get_full_text(self) -> str:
        """Get concatenated text from all chunks."""
        return "".join(self.chunks)


@dataclass
class StreamingState:
    """
    State for OpenAI streaming response transformation.

    Tracks the overall streaming session including multiple
    markdown block aggregators.
    """

    completion_id: str = field(
        default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:24]}"
    )
    created: int = field(default_factory=lambda: int(time.time()))
    model: str = ""

    # Chunk aggregators per markdown block (keyed by intended_usage)
    aggregators: dict[str, ChunkAggregator] = field(default_factory=dict)

    # Tracking
    has_sent_role: bool = False
    text_completed: bool = False

    def get_or_create_aggregator(self, intended_usage: str) -> ChunkAggregator:
        """Get or create aggregator for a specific markdown block."""
        if intended_usage not in self.aggregators:
            self.aggregators[intended_usage] = ChunkAggregator()
        return self.aggregators[intended_usage]

    def get_all_text(self) -> str:
        """Get concatenated text from all aggregators."""
        all_text = []
        for key in sorted(self.aggregators.keys()):
            all_text.append(self.aggregators[key].get_full_text())
        return "".join(all_text)

    def is_all_complete(self) -> bool:
        """Check if all aggregators are complete."""
        return self.text_completed or all(
            agg.is_complete for agg in self.aggregators.values()
        )
