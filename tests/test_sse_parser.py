"""Tests for Perplexity SSE parser."""

import pytest
from src.services.sse_parser import PerplexitySSEParser
from src.models.perplexity_models import (
    PerplexitySSEEvent,
    PerplexityBlock,
    DiffBlock,
    JSONPatch,
    MarkdownBlock,
)


class TestParseEventData:
    """Tests for parse_event_data method."""

    def test_parse_valid_event_with_blocks(self):
        """Should parse valid event data with blocks."""
        data = {
            "backend_uuid": "uuid-123",
            "uuid": "event-456",
            "display_model": "claude-4.5-sonnet",
            "mode": "copilot",
            "search_focus": "internet",
            "text_completed": False,
            "message_mode": "STREAMING",
            "thread_url_slug": "test-thread",
            "blocks": [
                {
                    "intended_usage": "ask_text_markdown",
                    "markdown_block": {
                        "progress": "IN_PROGRESS",
                        "chunks": ["Hello", " world"],
                    },
                }
            ],
        }

        event = PerplexitySSEParser.parse_event_data(data)

        assert event is not None
        assert isinstance(event, PerplexitySSEEvent)
        assert event.backend_uuid == "uuid-123"
        assert event.uuid == "event-456"
        assert event.display_model == "claude-4.5-sonnet"
        assert event.mode == "copilot"
        assert event.search_focus == "internet"
        assert event.text_completed is False
        assert event.message_mode == "STREAMING"
        assert event.thread_url_slug == "test-thread"
        assert len(event.blocks) == 1
        assert event.blocks[0].intended_usage == "ask_text_markdown"

    def test_parse_event_with_text_completed_true(self):
        """Should parse event with text_completed=True."""
        data = {
            "backend_uuid": "uuid-123",
            "uuid": "event-456",
            "text_completed": True,
            "blocks": [],
        }

        event = PerplexitySSEParser.parse_event_data(data)

        assert event is not None
        assert event.text_completed is True

    def test_parse_empty_event_data(self):
        """Should parse minimal/empty event data."""
        data = {}

        event = PerplexitySSEParser.parse_event_data(data)

        assert event is not None
        assert isinstance(event, PerplexitySSEEvent)
        assert event.backend_uuid == ""
        assert event.uuid == ""
        assert event.display_model == ""
        assert event.text_completed is False
        assert event.message_mode == "STREAMING"
        assert event.blocks == []

    def test_parse_event_with_empty_blocks_list(self):
        """Should handle event with empty blocks list."""
        data = {
            "backend_uuid": "uuid-123",
            "blocks": [],
        }

        event = PerplexitySSEParser.parse_event_data(data)

        assert event is not None
        assert event.blocks == []

    def test_parse_event_skips_invalid_blocks(self):
        """Should skip invalid blocks (those without intended_usage)."""
        data = {
            "blocks": [
                {"intended_usage": "ask_text_markdown", "markdown_block": {}},
                {"no_intended_usage": "skip_me"},  # Invalid - should be skipped
                {"intended_usage": "ask_text_0_markdown"},  # Valid - should be included
            ]
        }

        event = PerplexitySSEParser.parse_event_data(data)

        assert event is not None
        assert len(event.blocks) == 2
        assert event.blocks[0].intended_usage == "ask_text_markdown"
        assert event.blocks[1].intended_usage == "ask_text_0_markdown"

    def test_parse_event_handles_malformed_json(self):
        """Should return None for malformed/unparseable data."""
        # Pass None instead of dict
        result = PerplexitySSEParser.parse_event_data(None)
        assert result is None

    def test_parse_event_handles_exception_in_block_parsing(self):
        """Should return None if block parsing raises exception."""
        data = {
            "blocks": [
                {
                    "intended_usage": "ask_text_markdown",
                    "diff_block": {
                        "field": "markdown_block",
                        "patches": [
                            {
                                "op": "add",
                                "path": "/chunks/0",
                                # Missing 'value' - could cause issues
                            }
                        ],
                    },
                }
            ]
        }

        # Should still parse successfully despite the "invalid" patch
        event = PerplexitySSEParser.parse_event_data(data)
        assert event is not None
        assert len(event.blocks) == 1

    def test_parse_event_with_all_optional_fields(self):
        """Should parse event with all optional fields set."""
        data = {
            "backend_uuid": "backend-uuid",
            "uuid": "event-uuid",
            "display_model": "gpt-5.2",
            "mode": "search",
            "search_focus": "academic",
            "text_completed": True,
            "message_mode": "BATCH",
            "thread_url_slug": "my-thread",
            "blocks": [],
        }

        event = PerplexitySSEParser.parse_event_data(data)

        assert event.backend_uuid == "backend-uuid"
        assert event.uuid == "event-uuid"
        assert event.display_model == "gpt-5.2"
        assert event.mode == "search"
        assert event.search_focus == "academic"
        assert event.text_completed is True
        assert event.message_mode == "BATCH"
        assert event.thread_url_slug == "my-thread"


class TestParseBlock:
    """Tests for _parse_block method."""

    def test_parse_block_with_diff_block_and_patches(self):
        """Should parse block with diff_block containing patches."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "diff_block": {
                "field": "markdown_block",
                "patches": [
                    {
                        "op": "add",
                        "path": "/chunks/0",
                        "value": "Hello",
                    },
                    {
                        "op": "replace",
                        "path": "/progress",
                        "value": "DONE",
                    },
                ],
            },
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.intended_usage == "ask_text_markdown"
        assert block.diff_block is not None
        assert block.diff_block.field == "markdown_block"
        assert len(block.diff_block.patches) == 2
        assert block.diff_block.patches[0].op == "add"
        assert block.diff_block.patches[0].path == "/chunks/0"
        assert block.diff_block.patches[0].value == "Hello"
        assert block.diff_block.patches[1].op == "replace"
        assert block.diff_block.patches[1].value == "DONE"

    def test_parse_block_with_markdown_block(self):
        """Should parse block with markdown_block."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "markdown_block": {
                "progress": "IN_PROGRESS",
                "chunks": ["First chunk", "second chunk"],
                "chunk_starting_offset": 0,
                "answer": None,
            },
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.markdown_block is not None
        assert isinstance(block.markdown_block, MarkdownBlock)
        assert block.markdown_block.progress == "IN_PROGRESS"
        assert block.markdown_block.chunks == ["First chunk", "second chunk"]
        assert block.markdown_block.chunk_starting_offset == 0

    def test_parse_block_with_plan_block(self):
        """Should parse block with plan_block."""
        plan_data = {"steps": ["Step 1", "Step 2"], "total": 2}
        block_data = {
            "intended_usage": "ask_plan",
            "plan_block": plan_data,
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.plan_block == plan_data
        assert block.plan_block["steps"] == ["Step 1", "Step 2"]

    def test_parse_block_without_intended_usage_returns_none(self):
        """Should return None if block lacks intended_usage."""
        block_data = {
            "markdown_block": {"progress": "IN_PROGRESS"},
            # No intended_usage
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is None

    def test_parse_block_with_empty_intended_usage_returns_none(self):
        """Should return None if intended_usage is empty string."""
        block_data = {
            "intended_usage": "",
            "markdown_block": {"progress": "IN_PROGRESS"},
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is None

    def test_parse_block_with_invalid_diff_block_data(self):
        """Should handle invalid diff_block data gracefully."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "diff_block": {
                "field": "markdown_block",
                "patches": [
                    {
                        "op": "add",
                        # Missing path and value - but should still parse
                    }
                ],
            },
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.diff_block is not None
        assert len(block.diff_block.patches) == 1
        assert block.diff_block.patches[0].op == "add"
        assert block.diff_block.patches[0].path == ""

    def test_parse_block_with_empty_patches_list(self):
        """Should handle diff_block with no patches."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "diff_block": {
                "field": "markdown_block",
                "patches": [],
            },
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.diff_block is not None
        assert block.diff_block.patches == []

    def test_parse_block_without_diff_block(self):
        """Should parse block without diff_block field."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "markdown_block": {"progress": "DONE"},
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.diff_block is None

    def test_parse_block_with_all_block_types(self):
        """Should parse block with multiple block types."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "diff_block": {
                "field": "markdown_block",
                "patches": [{"op": "add", "path": "/chunks/0", "value": "text"}],
            },
            "markdown_block": {"progress": "IN_PROGRESS", "chunks": ["text"]},
            "plan_block": {"steps": ["Step 1"]},
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.diff_block is not None
        assert block.markdown_block is not None
        assert block.plan_block is not None

    def test_parse_block_with_invalid_type_raises_exception(self):
        """Should handle exception when block_data is not a dict."""
        result = PerplexitySSEParser._parse_block(None)
        assert result is None

    def test_parse_block_defaults_patch_op_to_replace(self):
        """Should default patch op to 'replace' when not provided."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "diff_block": {
                "field": "markdown_block",
                "patches": [
                    {
                        "path": "/chunks/0",
                        "value": "text",
                        # op not provided - should default
                    }
                ],
            },
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.diff_block.patches[0].op == "replace"

    def test_parse_block_defaults_diff_field_to_empty_string(self):
        """Should default diff_block field to empty string when not provided."""
        block_data = {
            "intended_usage": "ask_text_markdown",
            "diff_block": {
                "patches": [{"op": "add", "path": "/chunks/0", "value": "text"}]
                # field not provided
            },
        }

        block = PerplexitySSEParser._parse_block(block_data)

        assert block is not None
        assert block.diff_block.field == ""


class TestIsMarkdownBlock:
    """Tests for is_markdown_block method."""

    def test_ask_text_markdown_returns_true(self):
        """Should return True for 'ask_text_markdown'."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_markdown")
        assert result is True

    def test_ask_text_0_markdown_returns_true(self):
        """Should return True for 'ask_text_0_markdown'."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_0_markdown")
        assert result is True

    def test_ask_text_1_markdown_returns_true(self):
        """Should return True for 'ask_text_1_markdown'."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_1_markdown")
        assert result is True

    def test_ask_text_99_markdown_returns_true(self):
        """Should return True for any 'ask_text_N_markdown' pattern."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_99_markdown")
        assert result is True

    def test_ask_text_large_number_markdown_returns_true(self):
        """Should return True for large numbers in pattern."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_123456_markdown")
        assert result is True

    def test_other_block_type_returns_false(self):
        """Should return False for non-markdown block types."""
        result = PerplexitySSEParser.is_markdown_block("ask_plan")
        assert result is False

    def test_ask_text_without_markdown_suffix_returns_false(self):
        """Should return False for ask_text without _markdown suffix."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_0")
        assert result is False

    def test_empty_string_returns_false(self):
        """Should return False for empty string."""
        result = PerplexitySSEParser.is_markdown_block("")
        assert result is False

    def test_none_returns_false(self):
        """Should return False for None."""
        result = PerplexitySSEParser.is_markdown_block(None)
        assert result is False

    def test_wrong_prefix_markdown_returns_false(self):
        """Should return False for similar pattern with wrong prefix."""
        result = PerplexitySSEParser.is_markdown_block("ask_code_0_markdown")
        assert result is False

    def test_missing_underscore_returns_false(self):
        """Should return False for pattern missing underscores."""
        result = PerplexitySSEParser.is_markdown_block("ask_text0markdown")
        assert result is False

    def test_case_sensitive_matching(self):
        """Should be case-sensitive (uppercase should fail)."""
        result = PerplexitySSEParser.is_markdown_block("ASK_TEXT_MARKDOWN")
        assert result is False

    def test_extra_text_before_pattern_returns_false(self):
        """Should return False if pattern doesn't match exactly."""
        result = PerplexitySSEParser.is_markdown_block("prefix_ask_text_markdown")
        assert result is False

    def test_extra_text_after_pattern_returns_false(self):
        """Should return False if pattern doesn't match exactly."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_markdown_suffix")
        assert result is False

    def test_with_negative_number_returns_true(self):
        """Should return True even for negative numbers (pattern still matches)."""
        result = PerplexitySSEParser.is_markdown_block("ask_text_-1_markdown")
        assert result is True


class TestIterMarkdownBlocks:
    """Tests for iter_markdown_blocks method."""

    def test_iter_markdown_blocks_with_multiple_markdown_blocks(self):
        """Should yield all markdown blocks from event."""
        event = PerplexitySSEEvent(
            blocks=[
                PerplexityBlock(intended_usage="ask_text_markdown"),
                PerplexityBlock(intended_usage="ask_text_0_markdown"),
                PerplexityBlock(intended_usage="ask_plan"),  # Non-markdown
                PerplexityBlock(intended_usage="ask_text_1_markdown"),
            ]
        )

        blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks) == 3
        assert blocks[0].intended_usage == "ask_text_markdown"
        assert blocks[1].intended_usage == "ask_text_0_markdown"
        assert blocks[2].intended_usage == "ask_text_1_markdown"

    def test_iter_markdown_blocks_with_no_markdown_blocks(self):
        """Should yield nothing when event has no markdown blocks."""
        event = PerplexitySSEEvent(
            blocks=[
                PerplexityBlock(intended_usage="ask_plan"),
                PerplexityBlock(intended_usage="ask_code"),
            ]
        )

        blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks) == 0

    def test_iter_markdown_blocks_with_empty_blocks(self):
        """Should yield nothing when event has no blocks."""
        event = PerplexitySSEEvent(blocks=[])

        blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks) == 0

    def test_iter_markdown_blocks_returns_iterator(self):
        """Should return an iterator, not a list."""
        event = PerplexitySSEEvent(
            blocks=[PerplexityBlock(intended_usage="ask_text_markdown")]
        )

        result = PerplexitySSEParser.iter_markdown_blocks(event)

        # Should be an iterator/generator
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_iter_markdown_blocks_with_mixed_block_types(self):
        """Should only yield markdown blocks and ignore others."""
        event = PerplexitySSEEvent(
            blocks=[
                PerplexityBlock(intended_usage="ask_plan"),
                PerplexityBlock(intended_usage="ask_text_markdown"),
                PerplexityBlock(intended_usage="ask_code_0"),
                PerplexityBlock(intended_usage="ask_text_0_markdown"),
                PerplexityBlock(intended_usage="ask_other"),
            ]
        )

        blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks) == 2
        assert all(
            PerplexitySSEParser.is_markdown_block(block.intended_usage)
            for block in blocks
        )

    def test_iter_markdown_blocks_preserves_order(self):
        """Should preserve block order in output."""
        event = PerplexitySSEEvent(
            blocks=[
                PerplexityBlock(intended_usage="ask_text_2_markdown"),
                PerplexityBlock(intended_usage="ask_plan"),
                PerplexityBlock(intended_usage="ask_text_0_markdown"),
                PerplexityBlock(intended_usage="ask_text_1_markdown"),
            ]
        )

        blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks) == 3
        assert blocks[0].intended_usage == "ask_text_2_markdown"
        assert blocks[1].intended_usage == "ask_text_0_markdown"
        assert blocks[2].intended_usage == "ask_text_1_markdown"

    def test_iter_markdown_blocks_can_be_consumed_multiple_times(self):
        """Should create new iterator if called again."""
        event = PerplexitySSEEvent(
            blocks=[
                PerplexityBlock(intended_usage="ask_text_markdown"),
                PerplexityBlock(intended_usage="ask_plan"),
            ]
        )

        blocks1 = list(PerplexitySSEParser.iter_markdown_blocks(event))
        blocks2 = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks1) == 1
        assert len(blocks2) == 1
        assert blocks1[0].intended_usage == blocks2[0].intended_usage

    def test_iter_markdown_blocks_with_single_markdown_block(self):
        """Should yield single markdown block correctly."""
        event = PerplexitySSEEvent(
            blocks=[PerplexityBlock(intended_usage="ask_text_markdown")]
        )

        blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(blocks) == 1
        assert blocks[0].intended_usage == "ask_text_markdown"


class TestIntegration:
    """Integration tests combining multiple methods."""

    def test_parse_event_and_iter_markdown_blocks(self):
        """Should parse event and iterate markdown blocks correctly."""
        data = {
            "blocks": [
                {"intended_usage": "ask_text_markdown"},
                {"intended_usage": "ask_plan"},
                {"intended_usage": "ask_text_0_markdown"},
            ]
        }

        event = PerplexitySSEParser.parse_event_data(data)
        markdown_blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))

        assert len(markdown_blocks) == 2
        assert all(
            PerplexitySSEParser.is_markdown_block(block.intended_usage)
            for block in markdown_blocks
        )

    def test_full_parsing_pipeline_with_complex_data(self):
        """Should handle full parsing pipeline with realistic data."""
        data = {
            "backend_uuid": "backend-uuid",
            "uuid": "event-uuid",
            "display_model": "claude-4.5-sonnet",
            "text_completed": False,
            "blocks": [
                {
                    "intended_usage": "ask_text_markdown",
                    "markdown_block": {
                        "progress": "IN_PROGRESS",
                        "chunks": ["This is"],
                    },
                    "diff_block": {
                        "field": "markdown_block",
                        "patches": [
                            {
                                "op": "add",
                                "path": "/chunks/1",
                                "value": " the answer",
                            }
                        ],
                    },
                },
                {
                    "intended_usage": "ask_plan",
                    "plan_block": {"steps": ["Step 1"]},
                },
            ],
        }

        # Parse event
        event = PerplexitySSEParser.parse_event_data(data)
        assert event is not None
        assert len(event.blocks) == 2

        # Get markdown blocks
        markdown_blocks = list(PerplexitySSEParser.iter_markdown_blocks(event))
        assert len(markdown_blocks) == 1
        assert markdown_blocks[0].markdown_block is not None
        assert markdown_blocks[0].diff_block is not None
        assert markdown_blocks[0].diff_block.patches[0].value == " the answer"
