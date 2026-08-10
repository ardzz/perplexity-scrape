"""
Chunk extractor for Perplexity SSE streams.

Processes SSE events and extracts text chunks for OpenAI format conversion.
"""

import logging
from typing import Iterator, Optional

from src.models.perplexity_models import (
    PerplexityBlock,
    StreamingState,
)
from src.services.sse_parser import PerplexitySSEParser

logger = logging.getLogger(__name__)


class ChunkExtractor:
    """
    Extracts text chunks from Perplexity SSE events.

    This class processes the complex Perplexity SSE format and yields
    simple text chunks that can be converted to OpenAI format.
    """

    def __init__(self, state: Optional[StreamingState] = None):
        """
        Initialize the chunk extractor.

        Args:
            state: Optional streaming state. If not provided, creates a new one.
        """
        self.state = state or StreamingState()
        self._parser = PerplexitySSEParser()

    def process_event(self, event_data: dict) -> Iterator[str]:
        """
        Process a raw SSE event and yield text chunks.

        Args:
            event_data: The parsed JSON data from an SSE event

        Yields:
            Text chunks extracted from the event.
        """
        # Parse the event
        event = PerplexitySSEParser.parse_event_data(event_data)
        if not event:
            return

        # Update completion status
        if event.text_completed:
            self.state.text_completed = True

        # Update model if not set
        if not self.state.model and event.display_model:
            self.state.model = event.display_model

        # Process markdown blocks
        for block in PerplexitySSEParser.iter_markdown_blocks(event):
            yield from self._process_block(block)

    def _process_block(self, block: PerplexityBlock) -> Iterator[str]:
        """
        Process a single markdown block and yield text chunks.

        Args:
            block: The markdown block to process

        Yields:
            Text chunks from the block's patches.
        """
        # Get or create aggregator for this block
        aggregator = self.state.get_or_create_aggregator(block.intended_usage)

        # Current Perplexity responses send a complete markdown snapshot
        # directly, without JSON patches. ``answer`` is authoritative when
        # present; ``chunks`` remains the fallback for in-progress snapshots.
        if block.markdown_block:
            markdown = block.markdown_block
            snapshot: Optional[str] = None
            if markdown.answer:
                snapshot = markdown.answer
            elif markdown.chunks:
                snapshot = "".join(markdown.chunks)

            if snapshot is not None:
                current = aggregator.get_full_text()
                if snapshot != current:
                    new_text = (
                        snapshot[len(current) :]
                        if snapshot.startswith(current)
                        else snapshot
                    )
                    aggregator.chunks = [snapshot]
                    if new_text:
                        yield new_text

            if markdown.progress == "DONE":
                aggregator.is_complete = True

            if snapshot is not None:
                return

        if not block.diff_block:
            return

        # Apply each patch and yield new content
        for patch in block.diff_block.patches:
            new_text = aggregator.apply_patch(patch)
            if new_text:
                yield new_text

    def get_full_text(self) -> str:
        """
        Get the complete text from all processed events.

        Returns:
            The concatenated text from all aggregators.
        """
        return self.state.get_all_text()

    def is_complete(self) -> bool:
        """
        Check if the stream is complete.

        Returns:
            True if text_completed flag is set or all aggregators are done.
        """
        return self.state.is_all_complete()


def extract_chunks_from_events(events: Iterator[dict]) -> Iterator[str]:
    """
    Convenience function to extract chunks from a stream of events.

    Args:
        events: Iterator of parsed SSE event dictionaries

    Yields:
        Text chunks from the events.
    """
    extractor = ChunkExtractor()
    for event_data in events:
        yield from extractor.process_event(event_data)
