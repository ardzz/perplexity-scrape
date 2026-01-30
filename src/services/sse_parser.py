"""
Perplexity SSE parser.

Parses raw SSE events from Perplexity API and extracts structured blocks.
"""

import json
import logging
from typing import Optional, Iterator

from src.models.perplexity_models import (
    PerplexitySSEEvent,
    PerplexityBlock,
    DiffBlock,
    JSONPatch,
)

logger = logging.getLogger(__name__)


class PerplexitySSEParser:
    """
    Parser for Perplexity's SSE (Server-Sent Events) format.

    Perplexity sends events in this format:
    ```
    event: message
    data: {"blocks": [...], "text_completed": false, ...}
    ```
    """

    @staticmethod
    def parse_event_data(data: dict) -> Optional[PerplexitySSEEvent]:
        """
        Parse a raw event data dict into a structured PerplexitySSEEvent.

        Args:
            data: The parsed JSON data from an SSE event

        Returns:
            PerplexitySSEEvent if valid, None if parsing fails.
        """
        try:
            # Parse blocks
            blocks = []
            for block_data in data.get("blocks", []):
                block = PerplexitySSEParser._parse_block(block_data)
                if block:
                    blocks.append(block)

            return PerplexitySSEEvent(
                backend_uuid=data.get("backend_uuid", ""),
                uuid=data.get("uuid", ""),
                display_model=data.get("display_model", ""),
                mode=data.get("mode", ""),
                search_focus=data.get("search_focus", ""),
                text_completed=data.get("text_completed", False),
                message_mode=data.get("message_mode", "STREAMING"),
                blocks=blocks,
                thread_url_slug=data.get("thread_url_slug"),
            )
        except Exception as e:
            logger.debug(f"Failed to parse SSE event: {e}")
            return None

    @staticmethod
    def _parse_block(block_data: dict) -> Optional[PerplexityBlock]:
        """Parse a single block from event data."""
        try:
            intended_usage = block_data.get("intended_usage", "")
            if not intended_usage:
                return None

            diff_block = None
            if "diff_block" in block_data:
                diff_data = block_data["diff_block"]
                patches = []
                for patch_data in diff_data.get("patches", []):
                    patches.append(
                        JSONPatch(
                            op=patch_data.get("op", "replace"),
                            path=patch_data.get("path", ""),
                            value=patch_data.get("value"),
                        )
                    )
                diff_block = DiffBlock(
                    field=diff_data.get("field", ""),
                    patches=patches,
                )

            return PerplexityBlock(
                intended_usage=intended_usage,
                diff_block=diff_block,
                plan_block=block_data.get("plan_block"),
                markdown_block=block_data.get("markdown_block"),
            )
        except Exception as e:
            logger.debug(f"Failed to parse block: {e}")
            return None

    @staticmethod
    def is_markdown_block(intended_usage: str) -> bool:
        """
        Check if a block is a markdown answer block.

        Markdown answer blocks have intended_usage matching:
        - "ask_text_markdown" (combined answer)
        - "ask_text_N_markdown" where N is a number (individual sections)

        Args:
            intended_usage: The block's intended_usage field

        Returns:
            True if this is a markdown answer block.
        """
        if not intended_usage:
            return False

        # Match "ask_text_markdown" or "ask_text_N_markdown"
        if intended_usage == "ask_text_markdown":
            return True
        if intended_usage.startswith("ask_text_") and intended_usage.endswith(
            "_markdown"
        ):
            return True
        return False

    @staticmethod
    def iter_markdown_blocks(event: PerplexitySSEEvent) -> Iterator[PerplexityBlock]:
        """
        Iterate over markdown answer blocks in an event.

        Args:
            event: The parsed SSE event

        Yields:
            PerplexityBlock objects that contain markdown answer content.
        """
        for block in event.blocks:
            if PerplexitySSEParser.is_markdown_block(block.intended_usage):
                yield block
