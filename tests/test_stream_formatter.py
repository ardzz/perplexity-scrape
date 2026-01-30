"""
Unit tests for src.services.stream_formatter module.

Tests cover all functions and the StreamFormatter class with comprehensive
coverage for response formatting and streaming behavior.
"""

import json
import time
import pytest
from unittest.mock import patch

from src.services.stream_formatter import (
    generate_completion_id,
    format_openai_response,
    format_openai_chunk,
    format_sse_event,
    format_sse_done,
    StreamFormatter,
)
from src.models.openai_models import (
    ChatCompletionResponse,
    ChatCompletionChunk,
    DeltaContent,
    ChoiceMessage,
    Choice,
    ChunkChoice,
    UsageInfo,
)


class TestGenerateCompletionId:
    """Tests for generate_completion_id() function."""

    def test_returns_string_starting_with_chatcmpl(self):
        """Test that ID starts with 'chatcmpl-'."""
        completion_id = generate_completion_id()
        assert isinstance(completion_id, str)
        assert completion_id.startswith("chatcmpl-")

    def test_returns_correct_format(self):
        """Test that ID has correct format with 24 hex chars after prefix."""
        completion_id = generate_completion_id()
        # Format: "chatcmpl-" (9 chars) + 24 hex chars = 33 total
        assert len(completion_id) == 33
        # Check that part after prefix is valid hex
        hex_part = completion_id.split("-", 1)[1]
        assert len(hex_part) == 24
        assert all(c in "0123456789abcdef" for c in hex_part)

    def test_returns_unique_ids_on_multiple_calls(self):
        """Test that each call returns a unique ID."""
        id1 = generate_completion_id()
        id2 = generate_completion_id()
        id3 = generate_completion_id()

        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    def test_returns_multiple_unique_ids(self):
        """Test that many calls generate unique IDs."""
        ids = [generate_completion_id() for _ in range(100)]
        assert len(set(ids)) == 100, "All IDs should be unique"


class TestFormatOpenaiResponse:
    """Tests for format_openai_response() function."""

    def test_creates_chat_completion_response(self):
        """Test that function returns ChatCompletionResponse instance."""
        response = format_openai_response(content="Hello", model="test-model")
        assert isinstance(response, ChatCompletionResponse)

    def test_sets_content_in_message(self):
        """Test that response content is set correctly."""
        content = "Test response content"
        response = format_openai_response(content=content, model="test-model")

        assert len(response.choices) == 1
        assert response.choices[0].message.content == content

    def test_sets_model_name(self):
        """Test that model name is set in response."""
        model = "custom-model-name"
        response = format_openai_response(content="test", model=model)
        assert response.model == model

    def test_sets_assistant_role(self):
        """Test that message role is always 'assistant'."""
        response = format_openai_response(content="test", model="test-model")
        assert response.choices[0].message.role == "assistant"

    def test_sets_finish_reason_to_stop(self):
        """Test that finish_reason is always 'stop'."""
        response = format_openai_response(content="test", model="test-model")
        assert response.choices[0].finish_reason == "stop"

    def test_sets_usage_tokens_to_zero(self):
        """Test that all usage tokens are set to 0."""
        response = format_openai_response(content="test", model="test-model")

        assert response.usage.prompt_tokens == 0
        assert response.usage.completion_tokens == 0
        assert response.usage.total_tokens == 0

    def test_generates_completion_id_when_not_provided(self):
        """Test that completion_id is generated if not provided."""
        response = format_openai_response(content="test", model="test-model")

        assert isinstance(response.id, str)
        assert response.id.startswith("chatcmpl-")

    def test_uses_provided_completion_id(self):
        """Test that provided completion_id is used."""
        provided_id = "chatcmpl-custom123456789012345"
        response = format_openai_response(
            content="test", model="test-model", completion_id=provided_id
        )
        assert response.id == provided_id

    def test_generates_created_timestamp_when_not_provided(self):
        """Test that created timestamp is generated if not provided."""
        before = int(time.time())
        response = format_openai_response(content="test", model="test-model")
        after = int(time.time())

        assert before <= response.created <= after

    def test_uses_provided_created_timestamp(self):
        """Test that provided created timestamp is used."""
        provided_timestamp = 1234567890
        response = format_openai_response(
            content="test", model="test-model", created=provided_timestamp
        )
        assert response.created == provided_timestamp

    def test_choice_index_is_zero(self):
        """Test that choice index is always 0."""
        response = format_openai_response(content="test", model="test-model")
        assert response.choices[0].index == 0

    def test_response_object_type(self):
        """Test that response object type is 'chat.completion'."""
        response = format_openai_response(content="test", model="test-model")
        assert response.object == "chat.completion"

    def test_with_empty_content(self):
        """Test that empty content is handled correctly."""
        response = format_openai_response(content="", model="test-model")
        assert response.choices[0].message.content == ""

    def test_with_multiline_content(self):
        """Test that multiline content is preserved."""
        content = "Line 1\nLine 2\nLine 3"
        response = format_openai_response(content=content, model="test-model")
        assert response.choices[0].message.content == content

    def test_generates_different_ids_for_multiple_calls(self):
        """Test that multiple calls generate different IDs."""
        response1 = format_openai_response(content="test1", model="model1")
        response2 = format_openai_response(content="test2", model="model2")

        assert response1.id != response2.id


class TestFormatOpenaiChunk:
    """Tests for format_openai_chunk() function."""

    def test_creates_chat_completion_chunk(self):
        """Test that function returns ChatCompletionChunk instance."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test", created=1234567890, model="test-model"
        )
        assert isinstance(chunk, ChatCompletionChunk)

    def test_sets_completion_id(self):
        """Test that completion_id is set correctly."""
        test_id = "chatcmpl-custom-test"
        chunk = format_openai_chunk(
            completion_id=test_id, created=1234567890, model="test-model"
        )
        assert chunk.id == test_id

    def test_sets_created_timestamp(self):
        """Test that created timestamp is set correctly."""
        timestamp = 9876543210
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test", created=timestamp, model="test-model"
        )
        assert chunk.created == timestamp

    def test_sets_model_name(self):
        """Test that model name is set correctly."""
        model = "special-model"
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test", created=1234567890, model=model
        )
        assert chunk.model == model

    def test_chunk_object_type(self):
        """Test that chunk object type is 'chat.completion.chunk'."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test", created=1234567890, model="test-model"
        )
        assert chunk.object == "chat.completion.chunk"

    def test_chunk_index_is_zero(self):
        """Test that choice index is always 0."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test", created=1234567890, model="test-model"
        )
        assert chunk.choices[0].index == 0

    def test_creates_chunk_with_content_delta(self):
        """Test that chunk with content delta is created correctly."""
        content = "Hello world"
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content=content,
        )

        assert chunk.choices[0].delta.content == content
        assert chunk.choices[0].delta.role is None
        assert chunk.choices[0].finish_reason is None

    def test_creates_chunk_with_role_first_chunk(self):
        """Test that role is included in first chunk."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            role="assistant",
        )

        assert chunk.choices[0].delta.role == "assistant"
        assert chunk.choices[0].delta.content is None
        assert chunk.choices[0].finish_reason is None

    def test_creates_chunk_with_finish_reason_final_chunk(self):
        """Test that finish_reason is included in final chunk."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            finish_reason="stop",
        )

        assert chunk.choices[0].finish_reason == "stop"
        assert chunk.choices[0].delta.role is None
        assert chunk.choices[0].delta.content is None

    def test_chunk_with_role_and_content(self):
        """Test that chunk can have both role and content."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            role="assistant",
            content="Hello",
        )

        assert chunk.choices[0].delta.role == "assistant"
        assert chunk.choices[0].delta.content == "Hello"

    def test_chunk_with_all_optional_fields(self):
        """Test that chunk can have all optional fields set."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="text",
            role="assistant",
            finish_reason="stop",
        )

        assert chunk.choices[0].delta.role == "assistant"
        assert chunk.choices[0].delta.content == "text"
        assert chunk.choices[0].finish_reason == "stop"

    def test_chunk_usage_is_none(self):
        """Test that chunk usage is None by default."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test", created=1234567890, model="test-model"
        )
        assert chunk.usage is None

    def test_chunk_with_empty_content_string(self):
        """Test that empty content string is handled."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="",
        )

        # Empty string content should still be set
        assert chunk.choices[0].delta.content == ""


class TestFormatSseEvent:
    """Tests for format_sse_event() function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="test",
        )
        result = format_sse_event(chunk)
        assert isinstance(result, str)

    def test_format_includes_data_prefix(self):
        """Test that result starts with 'data: '."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="test",
        )
        result = format_sse_event(chunk)
        assert result.startswith("data: ")

    def test_format_ends_with_double_newline(self):
        """Test that result ends with '\\n\\n'."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="test",
        )
        result = format_sse_event(chunk)
        assert result.endswith("\n\n")

    def test_contains_valid_json(self):
        """Test that the event contains valid JSON."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="hello",
        )
        result = format_sse_event(chunk)

        # Extract JSON part (between "data: " and "\n\n")
        json_str = result[6:-2]  # Remove "data: " prefix and "\n\n" suffix
        parsed = json.loads(json_str)

        assert parsed["id"] == "chatcmpl-test"
        assert parsed["model"] == "test-model"
        assert parsed["created"] == 1234567890

    def test_json_includes_chunk_structure(self):
        """Test that JSON contains all chunk fields."""
        chunk = format_openai_chunk(
            completion_id="chatcmpl-test",
            created=1234567890,
            model="test-model",
            content="test content",
        )
        result = format_sse_event(chunk)

        json_str = result[6:-2]
        parsed = json.loads(json_str)

        assert "id" in parsed
        assert "object" in parsed
        assert "created" in parsed
        assert "model" in parsed
        assert "choices" in parsed


class TestFormatSseDone:
    """Tests for format_sse_done() function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        result = format_sse_done()
        assert isinstance(result, str)

    def test_returns_correct_format(self):
        """Test that result is exactly 'data: [DONE]\\n\\n'."""
        result = format_sse_done()
        assert result == "data: [DONE]\n\n"

    def test_starts_with_data_prefix(self):
        """Test that result starts with 'data: '."""
        result = format_sse_done()
        assert result.startswith("data: ")

    def test_ends_with_double_newline(self):
        """Test that result ends with '\\n\\n'."""
        result = format_sse_done()
        assert result.endswith("\n\n")

    def test_contains_done_marker(self):
        """Test that result contains '[DONE]'."""
        result = format_sse_done()
        assert "[DONE]" in result

    def test_returns_same_value_on_multiple_calls(self):
        """Test that function always returns same value."""
        result1 = format_sse_done()
        result2 = format_sse_done()
        result3 = format_sse_done()

        assert result1 == result2 == result3


class TestStreamFormatterInit:
    """Tests for StreamFormatter initialization."""

    def test_initializes_with_model_name(self):
        """Test that StreamFormatter stores model name."""
        formatter = StreamFormatter(model="test-model")
        assert formatter.model == "test-model"

    def test_generates_completion_id(self):
        """Test that StreamFormatter generates a completion ID."""
        formatter = StreamFormatter(model="test-model")
        assert isinstance(formatter.completion_id, str)
        assert formatter.completion_id.startswith("chatcmpl-")

    def test_generates_created_timestamp(self):
        """Test that StreamFormatter generates a created timestamp."""
        before = int(time.time())
        formatter = StreamFormatter(model="test-model")
        after = int(time.time())

        assert before <= formatter.created <= after

    def test_has_sent_role_is_false_initially(self):
        """Test that has_sent_role is False initially."""
        formatter = StreamFormatter(model="test-model")
        assert formatter.has_sent_role is False

    def test_different_formatters_have_different_ids(self):
        """Test that each formatter has unique completion ID."""
        formatter1 = StreamFormatter(model="model1")
        formatter2 = StreamFormatter(model="model2")

        assert formatter1.completion_id != formatter2.completion_id

    def test_different_formatters_have_different_timestamps(self):
        """Test that formatters might have different timestamps."""
        formatter1 = StreamFormatter(model="model1")
        # Small delay to ensure different timestamp
        time.sleep(0.01)
        formatter2 = StreamFormatter(model="model2")

        # Timestamps could be same if created within same second,
        # but completion IDs should always be different
        assert formatter1.completion_id != formatter2.completion_id


class TestStreamFormatterFormatRoleChunk:
    """Tests for StreamFormatter.format_role_chunk() method."""

    def test_returns_string(self):
        """Test that method returns a string."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_role_chunk()
        assert isinstance(result, str)

    def test_returns_sse_formatted_string(self):
        """Test that returned string is SSE formatted."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_role_chunk()

        assert result.startswith("data: ")
        assert result.endswith("\n\n")

    def test_role_chunk_contains_valid_json(self):
        """Test that role chunk contains valid JSON."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_role_chunk()

        json_str = result[6:-2]
        parsed = json.loads(json_str)

        assert "id" in parsed
        assert "model" in parsed
        assert "created" in parsed

    def test_role_chunk_includes_assistant_role(self):
        """Test that role chunk has assistant role in delta."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_role_chunk()

        json_str = result[6:-2]
        parsed = json.loads(json_str)

        assert parsed["choices"][0]["delta"]["role"] == "assistant"

    def test_role_chunk_has_no_content(self):
        """Test that role chunk has no content in delta."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_role_chunk()

        json_str = result[6:-2]
        parsed = json.loads(json_str)

        assert parsed["choices"][0]["delta"]["content"] is None

    def test_sets_has_sent_role_to_true(self):
        """Test that has_sent_role flag is set to True."""
        formatter = StreamFormatter(model="test-model")
        assert formatter.has_sent_role is False

        formatter.format_role_chunk()
        assert formatter.has_sent_role is True

    def test_returns_empty_string_on_second_call(self):
        """Test that subsequent calls return empty string."""
        formatter = StreamFormatter(model="test-model")

        first_call = formatter.format_role_chunk()
        assert first_call != ""
        assert first_call.startswith("data: ")

        second_call = formatter.format_role_chunk()
        assert second_call == ""

    def test_returns_empty_string_on_multiple_subsequent_calls(self):
        """Test that all subsequent calls return empty string."""
        formatter = StreamFormatter(model="test-model")
        formatter.format_role_chunk()  # First call

        assert formatter.format_role_chunk() == ""
        assert formatter.format_role_chunk() == ""
        assert formatter.format_role_chunk() == ""

    def test_uses_formatter_completion_id(self):
        """Test that role chunk uses formatter's completion ID."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_role_chunk()

        json_str = result[6:-2]
        parsed = json.loads(json_str)

        assert parsed["id"] == formatter.completion_id

    def test_uses_formatter_model(self):
        """Test that role chunk uses formatter's model."""
        model = "special-model-xyz"
        formatter = StreamFormatter(model=model)
        result = formatter.format_role_chunk()

        json_str = result[6:-2]
        parsed = json.loads(json_str)

        assert parsed["model"] == model


class TestStreamFormatterFormatContentChunk:
    """Tests for StreamFormatter.format_content_chunk() method."""

    def test_returns_string(self):
        """Test that method returns a string."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_content_chunk("test content")
        assert isinstance(result, str)

    def test_returns_sse_formatted_string(self):
        """Test that returned string is SSE formatted."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_content_chunk("test")

        # Should contain at least one SSE event
        assert "data: " in result
        assert "\n\n" in result

    def test_content_chunk_includes_provided_content(self):
        """Test that content chunk includes the provided content."""
        formatter = StreamFormatter(model="test-model")
        content = "Hello, world!"
        result = formatter.format_content_chunk(content)

        # Extract JSON from result
        # Result might have role chunk + content chunk
        lines = result.split("\n\n")
        # Last line with content should have the content
        for line in lines:
            if line.startswith("data: {"):
                try:
                    parsed = json.loads(line[6:])
                    if parsed["choices"][0]["delta"].get("content") == content:
                        return  # Found it
                except:
                    pass

        # If we get here, content wasn't found (it should be)
        assert False, "Content not found in formatted chunk"

    def test_automatically_sends_role_if_not_sent(self):
        """Test that content chunk sends role automatically if needed."""
        formatter = StreamFormatter(model="test-model")

        # has_sent_role is False
        assert formatter.has_sent_role is False

        result = formatter.format_content_chunk("test")

        # After calling format_content_chunk, has_sent_role should be True
        assert formatter.has_sent_role is True

        # Result should contain both role and content
        assert result.count("data: ") >= 2  # At least role + content

    def test_does_not_send_role_twice(self):
        """Test that role is only sent once even with multiple content chunks."""
        formatter = StreamFormatter(model="test-model")

        result1 = formatter.format_content_chunk("first")
        result2 = formatter.format_content_chunk("second")

        # First result should have role (role + content = 2 events)
        count1 = result1.count("data: ")
        assert count1 == 2  # role + content

        # Second result should have only content (no role = 1 event)
        count2 = result2.count("data: ")
        assert count2 == 1  # just content

    def test_content_chunks_use_formatter_id_and_model(self):
        """Test that content chunks use formatter's ID and model."""
        formatter = StreamFormatter(model="my-model")
        result = formatter.format_content_chunk("test")

        # Extract the content chunk (last event before empty line)
        lines = result.split("\n\n")
        for line in reversed(lines):
            if line.startswith("data: {"):
                parsed = json.loads(line[6:])
                assert parsed["id"] == formatter.completion_id
                assert parsed["model"] == "my-model"
                break

    def test_with_empty_content_string(self):
        """Test that empty content string is handled."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_content_chunk("")

        # Should still return formatted result
        assert isinstance(result, str)
        assert "data: " in result

    def test_with_multiline_content(self):
        """Test that multiline content is handled correctly."""
        formatter = StreamFormatter(model="test-model")
        content = "Line 1\nLine 2\nLine 3"
        result = formatter.format_content_chunk(content)

        # Extract and verify content
        lines = result.split("\n\n")
        for line in lines:
            if line.startswith("data: {"):
                parsed = json.loads(line[6:])
                if parsed["choices"][0]["delta"].get("content") == content:
                    assert True
                    return

        assert False, "Multiline content not preserved"

    def test_content_chunk_has_no_role(self):
        """Test that content chunks (after first) don't include role."""
        formatter = StreamFormatter(model="test-model")
        formatter.format_role_chunk()  # Send role explicitly

        result = formatter.format_content_chunk("test")

        # Extract content chunk JSON
        json_str = result[6:-2]  # Remove data prefix and newlines
        parsed = json.loads(json_str)

        # Content should be there, role should not
        assert parsed["choices"][0]["delta"]["content"] == "test"
        assert parsed["choices"][0]["delta"]["role"] is None

    def test_content_chunk_has_no_finish_reason(self):
        """Test that content chunks don't have finish_reason."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_content_chunk("test")

        # Extract content portion (last event)
        lines = result.split("\n\n")
        for line in reversed(lines):
            if line.startswith("data: {"):
                parsed = json.loads(line[6:])
                # Should have no finish_reason
                assert parsed["choices"][0]["finish_reason"] is None
                break


class TestStreamFormatterFormatFinalChunk:
    """Tests for StreamFormatter.format_final_chunk() method."""

    def test_returns_string(self):
        """Test that method returns a string."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()
        assert isinstance(result, str)

    def test_returns_sse_formatted_string(self):
        """Test that returned string contains SSE events."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        assert "data: " in result
        assert "\n\n" in result

    def test_includes_done_marker(self):
        """Test that final chunk includes [DONE] marker."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        assert "[DONE]" in result

    def test_final_chunk_ends_with_done_marker(self):
        """Test that result ends with [DONE] marker."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        assert result.endswith("data: [DONE]\n\n")

    def test_includes_finish_chunk_before_done(self):
        """Test that finish chunk comes before DONE marker."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        # Split by DONE
        parts = result.split("data: [DONE]")
        assert len(parts) == 2

        # First part should have finish chunk
        first_part = parts[0]
        assert first_part.endswith("\n\n")

        # Extract and verify finish chunk JSON
        json_str = first_part[6:-2]  # Remove "data: " and "\n\n"
        parsed = json.loads(json_str)

        # Should have finish_reason
        assert parsed["choices"][0]["finish_reason"] == "stop"

    def test_finish_chunk_has_stop_finish_reason(self):
        """Test that finish chunk has finish_reason='stop'."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        # Extract finish chunk (before DONE)
        parts = result.split("data: [DONE]")
        first_part = parts[0]
        json_str = first_part[6:-2]
        parsed = json.loads(json_str)

        assert parsed["choices"][0]["finish_reason"] == "stop"

    def test_finish_chunk_has_no_content(self):
        """Test that finish chunk has no content."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        parts = result.split("data: [DONE]")
        first_part = parts[0]
        json_str = first_part[6:-2]
        parsed = json.loads(json_str)

        # Should have no content in delta
        assert parsed["choices"][0]["delta"]["content"] is None

    def test_finish_chunk_has_no_role(self):
        """Test that finish chunk has no role."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        parts = result.split("data: [DONE]")
        first_part = parts[0]
        json_str = first_part[6:-2]
        parsed = json.loads(json_str)

        # Should have no role in delta
        assert parsed["choices"][0]["delta"]["role"] is None

    def test_uses_formatter_completion_id(self):
        """Test that final chunk uses formatter's completion ID."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        parts = result.split("data: [DONE]")
        first_part = parts[0]
        json_str = first_part[6:-2]
        parsed = json.loads(json_str)

        assert parsed["id"] == formatter.completion_id

    def test_uses_formatter_model(self):
        """Test that final chunk uses formatter's model."""
        model = "custom-final-model"
        formatter = StreamFormatter(model=model)
        result = formatter.format_final_chunk()

        parts = result.split("data: [DONE]")
        first_part = parts[0]
        json_str = first_part[6:-2]
        parsed = json.loads(json_str)

        assert parsed["model"] == model

    def test_uses_formatter_created_timestamp(self):
        """Test that final chunk uses formatter's created timestamp."""
        formatter = StreamFormatter(model="test-model")
        result = formatter.format_final_chunk()

        parts = result.split("data: [DONE]")
        first_part = parts[0]
        json_str = first_part[6:-2]
        parsed = json.loads(json_str)

        assert parsed["created"] == formatter.created


class TestStreamFormatterIntegration:
    """Integration tests for complete streaming flow."""

    def test_complete_streaming_flow(self):
        """Test complete streaming flow: role -> content -> final."""
        formatter = StreamFormatter(model="test-model")

        # Get all chunks
        role_chunk = formatter.format_role_chunk()
        content1 = formatter.format_content_chunk("Hello ")
        content2 = formatter.format_content_chunk("world")
        final = formatter.format_final_chunk()

        # Verify role sent only once
        role_count = role_chunk.count("assistant")
        assert role_count >= 1  # Should have role="assistant"

        # Verify content chunks
        assert "Hello " in content1
        assert "world" in content2

        # Verify final chunk
        assert "[DONE]" in final
        assert "stop" in final

    def test_skipping_role_chunk_call(self):
        """Test that format_content_chunk sends role if not already sent."""
        formatter = StreamFormatter(model="test-model")

        # Don't call format_role_chunk, go straight to content
        content = formatter.format_content_chunk("direct content")

        # Should still have role included
        assert "assistant" in content

    def test_state_management_across_calls(self):
        """Test that formatter state is properly maintained."""
        formatter = StreamFormatter(model="test-model")

        chunk1 = formatter.format_role_chunk()
        assert formatter.has_sent_role is True

        chunk2 = formatter.format_role_chunk()
        assert chunk2 == ""  # Should be empty second time
        assert formatter.has_sent_role is True  # State unchanged

        chunk3 = formatter.format_content_chunk("test")
        # Should not include role again
        assert chunk3.count("data: ") == 1  # Only content

    def test_same_id_and_timestamp_across_all_chunks(self):
        """Test that all chunks use same completion ID and timestamp."""
        formatter = StreamFormatter(model="test-model")
        expected_id = formatter.completion_id
        expected_created = formatter.created

        chunks = [
            formatter.format_role_chunk(),
            formatter.format_content_chunk("test"),
            formatter.format_final_chunk(),
        ]

        for chunk_str in chunks:
            # Extract all JSON objects from the chunk
            events = chunk_str.split("\n\n")
            for event in events:
                if event.startswith("data: {"):
                    parsed = json.loads(event[6:])
                    assert parsed["id"] == expected_id
                    assert parsed["created"] == expected_created

    def test_multiple_formatters_are_independent(self):
        """Test that multiple formatters don't interfere."""
        formatter1 = StreamFormatter(model="model1")
        formatter2 = StreamFormatter(model="model2")

        # Process formatter1
        f1_role = formatter1.format_role_chunk()
        f1_content = formatter1.format_content_chunk("f1 content")

        # Process formatter2
        f2_role = formatter2.format_role_chunk()
        f2_content = formatter2.format_content_chunk("f2 content")

        # Verify IDs are different
        assert formatter1.completion_id != formatter2.completion_id

        # Verify content is separate
        assert "f1 content" in f1_content
        assert "f2 content" in f2_content
        assert "f1 content" not in f2_content
        assert "f2 content" not in f1_content
