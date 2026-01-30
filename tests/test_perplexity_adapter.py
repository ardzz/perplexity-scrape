"""
Unit tests for src.services.perplexity_adapter.PerplexityAdapter

Tests cover:
- Initialization
- Message formatting (format_messages_as_query)
- Non-streaming completion (complete)
- Streaming completion (stream)

All tests use mocked PerplexityClient to avoid real API calls.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.services.perplexity_adapter import PerplexityAdapter
from src.models.openai_models import ChatMessage, MessageRole
from src.models.model_mapping import ModelConfig


class TestPerplexityAdapterInit:
    """Test PerplexityAdapter initialization."""

    def test_init_stores_client_reference(self):
        """Test that __init__ stores the client reference."""
        # Arrange
        mock_client = Mock()

        # Act
        adapter = PerplexityAdapter(client=mock_client)

        # Assert
        assert adapter._client is mock_client


class TestFormatMessagesAsQuery:
    """Test format_messages_as_query method."""

    def test_single_user_message_returns_content_directly(self):
        """Test that single user message returns content directly."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [ChatMessage(role=MessageRole.USER, content="Hello")]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        assert result == "Hello"

    def test_empty_messages_returns_empty_string(self):
        """Test that empty messages list returns empty string."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = []

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        assert result == ""

    def test_system_message_only_adds_context_prefix(self):
        """Test that system message alone adds [Context: ...] prefix."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="Be helpful and concise")
        ]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        assert result == "[Context: Be helpful and concise]"

    def test_system_and_user_message_format(self):
        """Test system + user message formatting."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="Be helpful"),
            ChatMessage(role=MessageRole.USER, content="What is AI?"),
        ]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        assert result == "[Context: Be helpful]\n\nUser: What is AI?"

    def test_user_and_assistant_messages_format_as_dialogue(self):
        """Test user + assistant messages format as dialogue."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [
            ChatMessage(role=MessageRole.USER, content="What is AI?"),
            ChatMessage(
                role=MessageRole.ASSISTANT, content="AI is artificial intelligence"
            ),
        ]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        assert "User: What is AI?" in result
        assert "Assistant: AI is artificial intelligence" in result

    def test_multiple_messages_with_system_formats_correctly(self):
        """Test system message with multi-turn conversation."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="You are helpful"),
            ChatMessage(role=MessageRole.USER, content="Hello"),
            ChatMessage(role=MessageRole.ASSISTANT, content="Hi there!"),
            ChatMessage(role=MessageRole.USER, content="How are you?"),
        ]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        assert result.startswith("[Context: You are helpful]")
        assert "User: Hello" in result
        assert "Assistant: Hi there!" in result
        assert "User: How are you?" in result

    def test_system_message_not_included_in_dialogue_section(self):
        """Test that system message doesn't appear in dialogue section."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="Be concise"),
            ChatMessage(role=MessageRole.USER, content="Test"),
        ]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        # System message should only appear in [Context: ...] part
        parts = result.split("\n\n")
        assert parts[0] == "[Context: Be concise]"
        assert parts[1] == "User: Test"

    def test_multiple_user_assistant_messages(self):
        """Test multi-turn conversation with alternating roles."""
        # Arrange
        adapter = PerplexityAdapter(client=Mock())
        messages = [
            ChatMessage(role=MessageRole.USER, content="First question"),
            ChatMessage(role=MessageRole.ASSISTANT, content="First answer"),
            ChatMessage(role=MessageRole.USER, content="Second question"),
            ChatMessage(role=MessageRole.ASSISTANT, content="Second answer"),
        ]

        # Act
        result = adapter.format_messages_as_query(messages)

        # Assert
        expected_lines = [
            "User: First question",
            "Assistant: First answer",
            "User: Second question",
            "Assistant: Second answer",
        ]
        for line in expected_lines:
            assert line in result


class TestComplete:
    """Test complete method (non-streaming)."""

    def test_complete_calls_client_ask_with_correct_params(self):
        """Test that complete() calls client.ask with correct parameters."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="Test response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Act
        result = adapter.complete(messages=messages, model="claude-4.5-sonnet")

        # Assert
        mock_client.ask.assert_called_once()
        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["query"] == "Test"
        assert call_kwargs["model_preference"] == "claude45sonnet"
        assert call_kwargs["is_incognito"] is True
        assert call_kwargs["mode"] == "copilot"
        assert call_kwargs["search_focus"] == "internet"

    def test_complete_returns_tuple_of_text_and_model(self):
        """Test that complete() returns (text, model_name) tuple."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="Test response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Act
        response_text, model_name = adapter.complete(
            messages=messages, model="claude-4.5-sonnet"
        )

        # Assert
        assert response_text == "Test response"
        assert model_name == "claude45sonnet"
        assert isinstance(response_text, str)
        assert isinstance(model_name, str)

    def test_complete_uses_different_models(self):
        """Test complete with different model configurations."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="Response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Test with different model
        adapter.complete(messages=messages, model="gpt-5.2")

        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["model_preference"] == "gpt52"

    def test_complete_formats_messages_as_query(self):
        """Test that complete() formats messages correctly."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="Response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="Be helpful"),
            ChatMessage(role=MessageRole.USER, content="Question"),
        ]

        # Act
        adapter.complete(messages=messages, model="claude45sonnetthinking")

        # Assert
        call_kwargs = mock_client.ask.call_args.kwargs
        query = call_kwargs["query"]
        assert "[Context: Be helpful]" in query
        assert "User: Question" in query

    def test_complete_uses_is_incognito_true(self):
        """Test that is_incognito is always True."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="Response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Act
        adapter.complete(messages=messages, model="claude45sonnetthinking")

        # Assert
        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["is_incognito"] is True

    def test_complete_with_empty_response_text(self):
        """Test complete with empty response text."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Act
        response_text, model_name = adapter.complete(
            messages=messages, model="claude45sonnetthinking"
        )

        # Assert
        assert response_text == ""
        assert model_name == "claude45sonnetthinking"

    def test_complete_returns_correct_perplexity_model_name(self):
        """Test that complete returns the perplexity model name, not openai name."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="Response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Act
        _, model_name = adapter.complete(
            messages=messages, model="claude-4.5-sonnet-thinking"
        )

        # Assert
        # Should return perplexity model name, not OpenAI name
        assert model_name == "claude45sonnetthinking"


class TestStream:
    """Test stream method (streaming completion)."""

    def test_stream_returns_generator_and_model_name(self):
        """Test that stream() returns (generator, model_name) tuple."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Act
        generator, model_name = adapter.stream(
            messages=messages, model="claude-4.5-sonnet"
        )

        # Assert
        assert hasattr(generator, "__iter__")
        assert model_name == "claude45sonnet"
        assert isinstance(model_name, str)

    def test_stream_generator_yields_chunks(self):
        """Test that the generator yields chunks from extractor."""
        # Arrange
        mock_client = Mock()
        mock_event_data = {"type": "event", "data": {}}
        mock_client.ask_stream.return_value = iter([mock_event_data])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Mock ChunkExtractor
        with patch(
            "src.services.perplexity_adapter.ChunkExtractor"
        ) as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            mock_extractor.process_event.return_value = iter(["chunk1", "chunk2"])

            # Act
            generator, _ = adapter.stream(
                messages=messages, model="claude45sonnetthinking"
            )
            chunks = list(generator)

            # Assert
            assert chunks == ["chunk1", "chunk2"]

    def test_stream_calls_client_ask_stream_with_correct_params(self):
        """Test that stream() calls client.ask_stream with correct parameters."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Mock ChunkExtractor to prevent iteration issues
        with patch("src.services.perplexity_adapter.ChunkExtractor"):
            # Act
            generator, _ = adapter.stream(messages=messages, model="claude-4.5-sonnet")
            # Consume generator to trigger ask_stream call
            list(generator)

            # Assert
            mock_client.ask_stream.assert_called_once()
            call_kwargs = mock_client.ask_stream.call_args.kwargs
            assert call_kwargs["query"] == "Test"
            assert call_kwargs["model_preference"] == "claude45sonnet"
            assert call_kwargs["is_incognito"] is True

    def test_stream_uses_is_incognito_true(self):
        """Test that stream always uses is_incognito=True."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Mock ChunkExtractor
        with patch("src.services.perplexity_adapter.ChunkExtractor"):
            # Act
            generator, _ = adapter.stream(
                messages=messages, model="claude45sonnetthinking"
            )
            list(generator)

            # Assert
            call_kwargs = mock_client.ask_stream.call_args.kwargs
            assert call_kwargs["is_incognito"] is True

    def test_stream_formats_messages_as_query(self):
        """Test that stream() formats messages correctly."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="Context"),
            ChatMessage(role=MessageRole.USER, content="Question"),
        ]

        # Mock ChunkExtractor
        with patch("src.services.perplexity_adapter.ChunkExtractor"):
            # Act
            generator, _ = adapter.stream(
                messages=messages, model="claude45sonnetthinking"
            )
            list(generator)

            # Assert
            call_kwargs = mock_client.ask_stream.call_args.kwargs
            query = call_kwargs["query"]
            assert "[Context: Context]" in query
            assert "User: Question" in query

    def test_stream_returns_correct_perplexity_model_name(self):
        """Test that stream returns the perplexity model name."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Mock ChunkExtractor
        with patch("src.services.perplexity_adapter.ChunkExtractor"):
            # Act
            _, model_name = adapter.stream(messages=messages, model="grok-4.1-thinking")

            # Assert
            assert model_name == "grok41reasoning"

    def test_stream_with_multiple_events(self):
        """Test stream processes multiple events correctly."""
        # Arrange
        mock_client = Mock()
        mock_events = [{"type": "event1"}, {"type": "event2"}, {"type": "event3"}]
        mock_client.ask_stream.return_value = iter(mock_events)

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Mock ChunkExtractor to track calls
        with patch(
            "src.services.perplexity_adapter.ChunkExtractor"
        ) as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            mock_extractor.process_event.side_effect = [
                iter(["a"]),
                iter(["b", "c"]),
                iter(["d"]),
            ]

            # Act
            generator, _ = adapter.stream(
                messages=messages, model="claude45sonnetthinking"
            )
            chunks = list(generator)

            # Assert
            assert chunks == ["a", "b", "c", "d"]
            assert mock_extractor.process_event.call_count == 3

    def test_stream_filters_empty_chunks(self):
        """Test that stream filters out empty chunks."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([{"type": "event"}])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]

        # Mock ChunkExtractor to return mix of empty and non-empty chunks
        with patch(
            "src.services.perplexity_adapter.ChunkExtractor"
        ) as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            mock_extractor.process_event.return_value = iter(
                ["chunk1", "", "chunk2", None, ""]
            )

            # Act
            generator, _ = adapter.stream(
                messages=messages, model="claude45sonnetthinking"
            )
            chunks = list(generator)

            # Assert
            # The implementation uses 'if chunk:' which filters empty strings and None
            assert "chunk1" in chunks
            assert "chunk2" in chunks
            assert "" not in chunks
            assert None not in chunks


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_adapter_workflow_complete(self):
        """Test complete workflow for non-streaming."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock(text="AI is artificial intelligence")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="Answer concisely"),
            ChatMessage(role=MessageRole.USER, content="What is AI?"),
        ]

        # Act
        response_text, model_name = adapter.complete(
            messages=messages, model="claude-4.5-sonnet"
        )

        # Assert
        assert response_text == "AI is artificial intelligence"
        assert model_name == "claude45sonnet"
        mock_client.ask.assert_called_once()

    def test_adapter_workflow_stream(self):
        """Test complete workflow for streaming."""
        # Arrange
        mock_client = Mock()
        mock_client.ask_stream.return_value = iter([{"type": "event"}])

        adapter = PerplexityAdapter(client=mock_client)
        messages = [
            ChatMessage(role=MessageRole.USER, content="Stream test"),
        ]

        # Mock ChunkExtractor
        with patch(
            "src.services.perplexity_adapter.ChunkExtractor"
        ) as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            mock_extractor.process_event.return_value = iter(["streaming", "response"])

            # Act
            generator, model_name = adapter.stream(
                messages=messages, model="claude-4.5-sonnet"
            )
            chunks = list(generator)

            # Assert
            assert chunks == ["streaming", "response"]
            assert model_name == "claude45sonnet"
            mock_client.ask_stream.assert_called_once()

    def test_different_model_mappings(self):
        """Test that different OpenAI models map to correct Perplexity models."""
        # Arrange
        test_cases = [
            ("claude-4.5-sonnet", "claude45sonnet"),
            ("claude-4.5-sonnet-thinking", "claude45sonnetthinking"),
            ("gpt-5.2", "gpt52"),
            ("gpt-5.2-thinking", "gpt52_thinking"),
            ("gemini-3-flash", "gemini30flash"),
            ("grok-4.1", "grok41nonreasoning"),
            ("grok-4.1-thinking", "grok41reasoning"),
        ]

        mock_client = Mock()
        mock_response = Mock(text="Response")
        mock_client.ask.return_value = mock_response

        adapter = PerplexityAdapter(client=mock_client)

        for openai_model, expected_perplexity_model in test_cases:
            # Act
            _, returned_model = adapter.complete(
                messages=[ChatMessage(role=MessageRole.USER, content="Test")],
                model=openai_model,
            )

            # Assert
            assert returned_model == expected_perplexity_model, (
                f"Model {openai_model} should map to {expected_perplexity_model}, "
                f"got {returned_model}"
            )
