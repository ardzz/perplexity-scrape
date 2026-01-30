"""
Unit tests for src/models/perplexity_models.py

Tests all Pydantic models and dataclasses for correct behavior,
focusing on functional correctness rather than pydantic validation.

Coverage target: 90%+
"""

import pytest
import time
from src.models.perplexity_models import (
    JSONPatch,
    DiffBlock,
    MarkdownBlock,
    PerplexityBlock,
    PerplexitySSEEvent,
    ChunkAggregator,
    StreamingState,
)


# ============================================================================
# JSONPatch Tests
# ============================================================================


class TestJSONPatch:
    """Tests for JSONPatch model."""

    def test_create_add_patch(self):
        """Test creating a JSONPatch with op='add'."""
        patch = JSONPatch(op="add", path="/chunks/0", value="text")
        assert patch.op == "add"
        assert patch.path == "/chunks/0"
        assert patch.value == "text"

    def test_create_replace_patch(self):
        """Test creating a JSONPatch with op='replace'."""
        patch = JSONPatch(op="replace", path="/progress", value="DONE")
        assert patch.op == "replace"
        assert patch.path == "/progress"
        assert patch.value == "DONE"

    def test_create_remove_patch(self):
        """Test creating a JSONPatch with op='remove'."""
        patch = JSONPatch(op="remove", path="/chunks/0")
        assert patch.op == "remove"
        assert patch.path == "/chunks/0"
        assert patch.value is None

    def test_patch_with_none_value(self):
        """Test JSONPatch with explicit None value."""
        patch = JSONPatch(op="add", path="/chunks/0", value=None)
        assert patch.value is None

    def test_patch_with_dict_value(self):
        """Test JSONPatch with dict value."""
        dict_val = {"chunks": ["a", "b"], "progress": "IN_PROGRESS"}
        patch = JSONPatch(op="replace", path="", value=dict_val)
        assert patch.value == dict_val

    def test_patch_with_numeric_value(self):
        """Test JSONPatch with numeric value."""
        patch = JSONPatch(op="add", path="/index", value=42)
        assert patch.value == 42


# ============================================================================
# DiffBlock Tests
# ============================================================================


class TestDiffBlock:
    """Tests for DiffBlock model."""

    def test_create_diffblock_with_field_and_patches(self):
        """Test creating DiffBlock with field and patches."""
        patches = [
            JSONPatch(op="add", path="/chunks/0", value="text"),
            JSONPatch(op="replace", path="/progress", value="DONE"),
        ]
        diff = DiffBlock(field="markdown_block", patches=patches)
        assert diff.field == "markdown_block"
        assert len(diff.patches) == 2
        assert diff.patches[0].op == "add"
        assert diff.patches[1].op == "replace"

    def test_create_diffblock_empty_patches(self):
        """Test creating DiffBlock with empty patches list."""
        diff = DiffBlock(field="markdown_block", patches=[])
        assert diff.field == "markdown_block"
        assert diff.patches == []

    def test_create_diffblock_default_patches(self):
        """Test DiffBlock defaults patches to empty list."""
        diff = DiffBlock(field="plan_block")
        assert diff.field == "plan_block"
        assert diff.patches == []


# ============================================================================
# MarkdownBlock Tests
# ============================================================================


class TestMarkdownBlock:
    """Tests for MarkdownBlock model."""

    def test_default_progress_in_progress(self):
        """Test MarkdownBlock defaults progress to IN_PROGRESS."""
        block = MarkdownBlock()
        assert block.progress == "IN_PROGRESS"

    def test_progress_done(self):
        """Test MarkdownBlock with progress=DONE."""
        block = MarkdownBlock(progress="DONE")
        assert block.progress == "DONE"

    def test_with_chunks_list(self):
        """Test MarkdownBlock with chunks list."""
        chunks = ["Hello ", "world ", "!"]
        block = MarkdownBlock(chunks=chunks)
        assert block.chunks == chunks

    def test_default_chunks_empty(self):
        """Test MarkdownBlock defaults chunks to empty list."""
        block = MarkdownBlock()
        assert block.chunks == []

    def test_all_fields(self):
        """Test MarkdownBlock with all fields populated."""
        block = MarkdownBlock(
            progress="DONE",
            chunks=["a", "b"],
            chunk_starting_offset=5,
            answer="full answer",
            media_items=[{"type": "image"}],
            inline_token_annotations=[{"start": 0}],
        )
        assert block.progress == "DONE"
        assert block.chunks == ["a", "b"]
        assert block.chunk_starting_offset == 5
        assert block.answer == "full answer"
        assert block.media_items == [{"type": "image"}]
        assert block.inline_token_annotations == [{"start": 0}]


# ============================================================================
# PerplexityBlock Tests
# ============================================================================


class TestPerplexityBlock:
    """Tests for PerplexityBlock model."""

    def test_with_diff_block(self):
        """Test PerplexityBlock with diff_block."""
        diff = DiffBlock(field="markdown_block")
        block = PerplexityBlock(intended_usage="answer", diff_block=diff)
        assert block.intended_usage == "answer"
        assert block.diff_block == diff
        assert block.plan_block is None
        assert block.markdown_block is None

    def test_with_markdown_block(self):
        """Test PerplexityBlock with markdown_block."""
        markdown = MarkdownBlock(chunks=["response"])
        block = PerplexityBlock(intended_usage="answer", markdown_block=markdown)
        assert block.intended_usage == "answer"
        assert block.markdown_block == markdown
        assert block.diff_block is None
        assert block.plan_block is None

    def test_with_plan_block(self):
        """Test PerplexityBlock with plan_block."""
        plan = {"steps": ["step1", "step2"]}
        block = PerplexityBlock(intended_usage="plan", plan_block=plan)
        assert block.intended_usage == "plan"
        assert block.plan_block == plan
        assert block.diff_block is None
        assert block.markdown_block is None

    def test_all_blocks_none(self):
        """Test PerplexityBlock with no blocks."""
        block = PerplexityBlock(intended_usage="test")
        assert block.intended_usage == "test"
        assert block.diff_block is None
        assert block.markdown_block is None
        assert block.plan_block is None


# ============================================================================
# PerplexitySSEEvent Tests
# ============================================================================


class TestPerplexitySSEEvent:
    """Tests for PerplexitySSEEvent model."""

    def test_full_event_with_all_fields(self):
        """Test PerplexitySSEEvent with all fields populated."""
        blocks = [
            PerplexityBlock(
                intended_usage="answer", markdown_block=MarkdownBlock(chunks=["text"])
            )
        ]
        event = PerplexitySSEEvent(
            backend_uuid="uuid-123",
            uuid="uuid-456",
            display_model="claude-4.5-sonnet",
            mode="copilot",
            search_focus="internet",
            text_completed=True,
            message_mode="STREAMING",
            blocks=blocks,
            thread_url_slug="thread-123",
        )
        assert event.backend_uuid == "uuid-123"
        assert event.uuid == "uuid-456"
        assert event.display_model == "claude-4.5-sonnet"
        assert event.mode == "copilot"
        assert event.search_focus == "internet"
        assert event.text_completed is True
        assert event.message_mode == "STREAMING"
        assert len(event.blocks) == 1
        assert event.thread_url_slug == "thread-123"

    def test_default_values(self):
        """Test PerplexitySSEEvent defaults."""
        event = PerplexitySSEEvent()
        assert event.backend_uuid == ""
        assert event.uuid == ""
        assert event.display_model == ""
        assert event.mode == ""
        assert event.search_focus == ""
        assert event.text_completed is False
        assert event.message_mode == "STREAMING"
        assert event.blocks == []
        assert event.thread_url_slug is None

    def test_event_with_multiple_blocks(self):
        """Test PerplexitySSEEvent with multiple blocks."""
        blocks = [
            PerplexityBlock(intended_usage="answer"),
            PerplexityBlock(intended_usage="plan"),
            PerplexityBlock(intended_usage="search"),
        ]
        event = PerplexitySSEEvent(blocks=blocks)
        assert len(event.blocks) == 3


# ============================================================================
# ChunkAggregator Tests
# ============================================================================


class TestChunkAggregator:
    """Tests for ChunkAggregator dataclass."""

    def test_apply_patch_add_chunk(self):
        """Test apply_patch with 'add' op adds chunk to list."""
        agg = ChunkAggregator()
        patch = JSONPatch(op="add", path="/chunks/0", value="hello")
        result = agg.apply_patch(patch)

        assert result == "hello"
        assert agg.chunks == ["hello"]
        assert agg.is_complete is False

    def test_apply_patch_multiple_adds(self):
        """Test apply_patch with multiple 'add' operations."""
        agg = ChunkAggregator()
        patches = [
            JSONPatch(op="add", path="/chunks/0", value="hello"),
            JSONPatch(op="add", path="/chunks/1", value=" "),
            JSONPatch(op="add", path="/chunks/2", value="world"),
        ]
        for patch in patches:
            agg.apply_patch(patch)

        assert agg.chunks == ["hello", " ", "world"]

    def test_apply_patch_replace_progress_done(self):
        """Test apply_patch with 'replace' path=/progress value=DONE."""
        agg = ChunkAggregator()
        patch = JSONPatch(op="replace", path="/progress", value="DONE")
        result = agg.apply_patch(patch)

        assert result is None
        assert agg.is_complete is True

    def test_apply_patch_replace_initial_chunks(self):
        """Test apply_patch with 'replace' path='' extracts initial chunks."""
        agg = ChunkAggregator()
        patch = JSONPatch(
            op="replace", path="", value={"chunks": ["initial ", "chunks"]}
        )
        result = agg.apply_patch(patch)

        assert result == "initial chunks"
        assert agg.chunks == ["initial ", "chunks"]

    def test_apply_patch_replace_initial_chunks_empty(self):
        """Test apply_patch with 'replace' path='' and empty chunks."""
        agg = ChunkAggregator()
        patch = JSONPatch(op="replace", path="", value={"chunks": []})
        result = agg.apply_patch(patch)

        assert result is None
        assert agg.chunks == []

    def test_apply_patch_remove_no_effect(self):
        """Test apply_patch with 'remove' op has no effect."""
        agg = ChunkAggregator()
        patch = JSONPatch(op="remove", path="/chunks/0")
        result = agg.apply_patch(patch)

        assert result is None
        assert agg.chunks == []

    def test_apply_patch_add_with_none_value(self):
        """Test apply_patch with 'add' and None value."""
        agg = ChunkAggregator()
        patch = JSONPatch(op="add", path="/chunks/0", value=None)
        result = agg.apply_patch(patch)

        assert result == ""
        assert agg.chunks == [""]

    def test_apply_patch_add_with_numeric_value(self):
        """Test apply_patch with 'add' and numeric value."""
        agg = ChunkAggregator()
        patch = JSONPatch(op="add", path="/chunks/0", value=42)
        result = agg.apply_patch(patch)

        assert result == "42"
        assert agg.chunks == ["42"]

    def test_get_full_text_empty(self):
        """Test get_full_text with no chunks."""
        agg = ChunkAggregator()
        assert agg.get_full_text() == ""

    def test_get_full_text_concatenates_chunks(self):
        """Test get_full_text concatenates all chunks."""
        agg = ChunkAggregator(chunks=["hello", " ", "world", "!"])
        assert agg.get_full_text() == "hello world!"

    def test_get_full_text_after_patches(self):
        """Test get_full_text after applying patches."""
        agg = ChunkAggregator()
        patches = [
            JSONPatch(op="add", path="/chunks/0", value="The "),
            JSONPatch(op="add", path="/chunks/1", value="answer "),
            JSONPatch(op="add", path="/chunks/2", value="is 42"),
        ]
        for patch in patches:
            agg.apply_patch(patch)

        assert agg.get_full_text() == "The answer is 42"

    def test_is_complete_initially_false(self):
        """Test is_complete defaults to False."""
        agg = ChunkAggregator()
        assert agg.is_complete is False

    def test_is_complete_set_by_patch(self):
        """Test is_complete is set by progress=DONE patch."""
        agg = ChunkAggregator()
        assert agg.is_complete is False

        patch = JSONPatch(op="replace", path="/progress", value="DONE")
        agg.apply_patch(patch)

        assert agg.is_complete is True


# ============================================================================
# StreamingState Tests
# ============================================================================


class TestStreamingState:
    """Tests for StreamingState dataclass."""

    def test_default_creation(self):
        """Test StreamingState default creation."""
        state = StreamingState()
        assert state.completion_id.startswith("chatcmpl-")
        assert isinstance(state.created, int)
        assert state.created > 0
        assert state.model == ""
        assert state.aggregators == {}
        assert state.has_sent_role is False
        assert state.text_completed is False

    def test_get_or_create_aggregator_creates_new(self):
        """Test get_or_create_aggregator creates new aggregator."""
        state = StreamingState()
        agg = state.get_or_create_aggregator("answer")

        assert isinstance(agg, ChunkAggregator)
        assert agg.chunks == []
        assert agg.is_complete is False
        assert "answer" in state.aggregators

    def test_get_or_create_aggregator_returns_existing(self):
        """Test get_or_create_aggregator returns existing aggregator."""
        state = StreamingState()
        agg1 = state.get_or_create_aggregator("answer")

        # Add some chunks to first aggregator
        patch = JSONPatch(op="add", path="/chunks/0", value="text")
        agg1.apply_patch(patch)

        # Get same aggregator
        agg2 = state.get_or_create_aggregator("answer")

        assert agg1 is agg2
        assert agg2.chunks == ["text"]

    def test_get_or_create_aggregator_multiple_keys(self):
        """Test get_or_create_aggregator with multiple keys."""
        state = StreamingState()
        agg1 = state.get_or_create_aggregator("answer")
        agg2 = state.get_or_create_aggregator("plan")
        agg3 = state.get_or_create_aggregator("search")

        assert len(state.aggregators) == 3
        assert agg1 is not agg2
        assert agg2 is not agg3

    def test_get_all_text_empty(self):
        """Test get_all_text with no aggregators."""
        state = StreamingState()
        assert state.get_all_text() == ""

    def test_get_all_text_single_aggregator(self):
        """Test get_all_text with single aggregator."""
        state = StreamingState()
        agg = state.get_or_create_aggregator("answer")
        agg.chunks = ["hello", " ", "world"]

        assert state.get_all_text() == "hello world"

    def test_get_all_text_multiple_aggregators_sorted(self):
        """Test get_all_text concatenates from all aggregators in sorted order."""
        state = StreamingState()

        # Create aggregators in non-alphabetical order
        agg_search = state.get_or_create_aggregator("search")
        agg_answer = state.get_or_create_aggregator("answer")
        agg_plan = state.get_or_create_aggregator("plan")

        agg_answer.chunks = ["answer"]
        agg_plan.chunks = ["plan"]
        agg_search.chunks = ["search"]

        # Should be concatenated in alphabetical order: answer, plan, search
        assert state.get_all_text() == "answerplansearch"

    def test_get_all_text_multiple_aggregators_order(self):
        """Test get_all_text respects alphabetical order."""
        state = StreamingState()
        agg_z = state.get_or_create_aggregator("zebra")
        agg_a = state.get_or_create_aggregator("apple")
        agg_m = state.get_or_create_aggregator("middle")

        agg_z.chunks = ["z"]
        agg_a.chunks = ["a"]
        agg_m.chunks = ["m"]

        assert state.get_all_text() == "amz"

    def test_is_all_complete_text_completed_true(self):
        """Test is_all_complete returns True when text_completed=True."""
        state = StreamingState()
        state.get_or_create_aggregator("answer")

        assert state.is_all_complete() is False
        state.text_completed = True
        assert state.is_all_complete() is True

    def test_is_all_complete_all_aggregators_complete(self):
        """Test is_all_complete with all aggregators marked complete."""
        state = StreamingState()
        agg1 = state.get_or_create_aggregator("answer")
        agg2 = state.get_or_create_aggregator("plan")

        agg1.is_complete = True
        agg2.is_complete = True

        assert state.is_all_complete() is True

    def test_is_all_complete_one_incomplete(self):
        """Test is_all_complete with one incomplete aggregator."""
        state = StreamingState()
        agg1 = state.get_or_create_aggregator("answer")
        agg2 = state.get_or_create_aggregator("plan")

        agg1.is_complete = True
        agg2.is_complete = False

        assert state.is_all_complete() is False

    def test_is_all_complete_no_aggregators(self):
        """Test is_all_complete with no aggregators."""
        state = StreamingState()
        assert state.is_all_complete() is True  # all() on empty list is True

    def test_completion_id_unique(self):
        """Test that each StreamingState gets unique completion_id."""
        state1 = StreamingState()
        state2 = StreamingState()

        assert state1.completion_id != state2.completion_id

    def test_created_timestamp_recent(self):
        """Test that created timestamp is recent."""
        before = int(time.time())
        state = StreamingState()
        after = int(time.time())

        assert before <= state.created <= after


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple models."""

    def test_full_streaming_workflow(self):
        """Test a complete streaming workflow."""
        state = StreamingState(model="claude-4.5-sonnet")

        # Create answer aggregator and add chunks
        answer_agg = state.get_or_create_aggregator("answer")
        answer_agg.apply_patch(JSONPatch(op="add", path="/chunks/0", value="Hello "))
        answer_agg.apply_patch(JSONPatch(op="add", path="/chunks/1", value="world"))

        # Create plan aggregator
        plan_agg = state.get_or_create_aggregator("plan")
        plan_agg.apply_patch(JSONPatch(op="add", path="/chunks/0", value="Plan text"))

        # Mark answer complete
        answer_agg.apply_patch(JSONPatch(op="replace", path="/progress", value="DONE"))

        assert state.get_all_text() == "Hello worldPlan text"
        assert state.is_all_complete() is False  # plan not complete

        # Mark plan complete
        plan_agg.apply_patch(JSONPatch(op="replace", path="/progress", value="DONE"))
        assert state.is_all_complete() is True

    def test_sse_event_to_streaming_state(self):
        """Test converting PerplexitySSEEvent data to StreamingState."""
        # Create event
        event = PerplexitySSEEvent(
            backend_uuid="test-uuid",
            display_model="claude-4.5-sonnet",
            blocks=[
                PerplexityBlock(
                    intended_usage="answer",
                    diff_block=DiffBlock(
                        field="markdown_block",
                        patches=[
                            JSONPatch(op="add", path="/chunks/0", value="Response ")
                        ],
                    ),
                )
            ],
        )

        # Create state
        state = StreamingState(model=event.display_model)

        # Process event
        for block in event.blocks:
            if block.diff_block:
                agg = state.get_or_create_aggregator(block.intended_usage)
                for patch in block.diff_block.patches:
                    agg.apply_patch(patch)

        assert state.get_all_text() == "Response "

    def test_chunk_aggregator_with_initial_block(self):
        """Test ChunkAggregator handling initial block setup."""
        agg = ChunkAggregator()

        # Initial block setup patch
        initial_patch = JSONPatch(
            op="replace",
            path="",
            value={"progress": "IN_PROGRESS", "chunks": ["Initial ", "content"]},
        )
        agg.apply_patch(initial_patch)

        # Add more chunks
        add_patch = JSONPatch(op="add", path="/chunks/2", value=" appended")
        agg.apply_patch(add_patch)

        assert agg.get_full_text() == "Initial content appended"
        assert agg.is_complete is False

        # Mark complete
        complete_patch = JSONPatch(op="replace", path="/progress", value="DONE")
        agg.apply_patch(complete_patch)

        assert agg.is_complete is True
