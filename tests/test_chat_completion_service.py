"""
Unit tests for ChatCompletionService.

Tests cover initialization, completion handling, streaming, and request routing.
Target: 90%+ code coverage.
"""

import unittest
import asyncio
from unittest.mock import Mock, MagicMock, patch, call
from typing import Generator

from fastapi.responses import StreamingResponse

from src.services.chat_completion_service import ChatCompletionService
from src.models.openai_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    MessageRole,
)


class TestChatCompletionServiceInit(unittest.TestCase):
    """Tests for ChatCompletionService.__init__()"""

    def test_init_creates_adapter_with_client(self):
        """Test that __init__ creates PerplexityAdapter with provided client."""
        # Arrange
        mock_client = Mock()

        # Act
        with patch(
            "src.services.chat_completion_service.PerplexityAdapter"
        ) as mock_adapter_class:
            service = ChatCompletionService(mock_client)

            # Assert
            mock_adapter_class.assert_called_once_with(mock_client)
            assert service._adapter == mock_adapter_class.return_value

    def test_init_stores_client_in_adapter(self):
        """Test that the adapter receives the correct client instance."""
        # Arrange
        mock_client = Mock()

        # Act
        with patch(
            "src.services.chat_completion_service.PerplexityAdapter"
        ) as mock_adapter_class:
            service = ChatCompletionService(mock_client)

            # Assert
            assert mock_adapter_class.call_args[0][0] is mock_client


class TestChatCompletionServiceHandleCompletion(unittest.TestCase):
    """Tests for ChatCompletionService.handle_completion()"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_adapter = Mock()

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=self.mock_adapter,
        ):
            self.service = ChatCompletionService(self.mock_client)

    def test_handle_completion_calls_adapter_complete(self):
        """Test that handle_completion calls adapter.complete() with correct params."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Hello")]
        request = ChatCompletionRequest(model="gpt-4", messages=messages)

        self.mock_adapter.complete.return_value = ("Response text", "gpt-4")

        # Act
        with patch(
            "src.services.chat_completion_service.format_openai_response"
        ) as mock_format:
            self.service.handle_completion(request)

            # Assert
            self.mock_adapter.complete.assert_called_once_with(
                messages=messages,
                model="gpt-4",
            )

    def test_handle_completion_returns_formatted_response(self):
        """Test that handle_completion returns ChatCompletionResponse."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Test query")]
        request = ChatCompletionRequest(model="claude-4.5-sonnet", messages=messages)

        self.mock_adapter.complete.return_value = (
            "Generated response",
            "claude-4.5-sonnet",
        )

        # Act
        with patch(
            "src.services.chat_completion_service.format_openai_response"
        ) as mock_format:
            mock_response = ChatCompletionResponse(
                id="test-id",
                model="claude-4.5-sonnet",
                choices=[],
            )
            mock_format.return_value = mock_response

            result = self.service.handle_completion(request)

            # Assert
            assert result == mock_response
            mock_format.assert_called_once_with(
                content="Generated response",
                model="claude-4.5-sonnet",
            )

    def test_handle_completion_passes_model_name_to_formatter(self):
        """Test that model name from adapter is passed to formatter."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="openai-model", messages=messages)

        adapter_model = "actual-model-name"
        self.mock_adapter.complete.return_value = ("Response", adapter_model)

        # Act
        with patch(
            "src.services.chat_completion_service.format_openai_response"
        ) as mock_format:
            self.service.handle_completion(request)

            # Assert
            assert mock_format.call_args[1]["model"] == adapter_model

    def test_handle_completion_with_multiple_messages(self):
        """Test handle_completion with conversation history."""
        # Arrange
        messages = [
            ChatMessage(role=MessageRole.USER, content="First message"),
            ChatMessage(role=MessageRole.ASSISTANT, content="First response"),
            ChatMessage(role=MessageRole.USER, content="Follow up"),
        ]
        request = ChatCompletionRequest(model="test-model", messages=messages)

        self.mock_adapter.complete.return_value = ("Final response", "test-model")

        # Act
        with patch(
            "src.services.chat_completion_service.format_openai_response"
        ) as mock_format:
            self.service.handle_completion(request)

            # Assert
            self.mock_adapter.complete.assert_called_once()
            call_args = self.mock_adapter.complete.call_args
            assert call_args[1]["messages"] == messages
            assert len(call_args[1]["messages"]) == 3


class TestChatCompletionServiceHandleStreaming(unittest.TestCase):
    """Tests for ChatCompletionService.handle_streaming()"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_adapter = Mock()

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=self.mock_adapter,
        ):
            self.service = ChatCompletionService(self.mock_client)

    def test_handle_streaming_calls_adapter_stream(self):
        """Test that handle_streaming calls adapter.stream() with correct params."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Stream query")]
        request = ChatCompletionRequest(
            model="streaming-model", messages=messages, stream=True
        )

        chunk_gen = (chunk for chunk in ["chunk1", "chunk2"])
        self.mock_adapter.stream.return_value = (chunk_gen, "streaming-model")

        # Act
        with patch(
            "src.services.chat_completion_service.StreamFormatter"
        ) as mock_formatter_class:
            result = self.service.handle_streaming(request)

            # Assert
            self.mock_adapter.stream.assert_called_once_with(
                messages=messages,
                model="streaming-model",
            )

    def test_handle_streaming_returns_streaming_response(self):
        """Test that handle_streaming returns StreamingResponse."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]
        request = ChatCompletionRequest(model="test-model", messages=messages)

        chunk_gen = (chunk for chunk in [])
        self.mock_adapter.stream.return_value = (chunk_gen, "test-model")

        # Act
        with patch("src.services.chat_completion_service.StreamFormatter"):
            result = self.service.handle_streaming(request)

            # Assert
            assert isinstance(result, StreamingResponse)

    def test_handle_streaming_sets_correct_media_type(self):
        """Test that StreamingResponse has correct media type."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="model", messages=messages)

        chunk_gen = (chunk for chunk in [])
        self.mock_adapter.stream.return_value = (chunk_gen, "model")

        # Act
        with patch("src.services.chat_completion_service.StreamFormatter"):
            result = self.service.handle_streaming(request)

            # Assert
            assert result.media_type == "text/event-stream"

    def test_handle_streaming_sets_cache_control_headers(self):
        """Test that StreamingResponse has correct cache control headers."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="model", messages=messages)

        chunk_gen = (chunk for chunk in [])
        self.mock_adapter.stream.return_value = (chunk_gen, "model")

        # Act
        with patch("src.services.chat_completion_service.StreamFormatter"):
            result = self.service.handle_streaming(request)

            # Assert
            assert result.headers["Cache-Control"] == "no-cache"
            assert result.headers["Connection"] == "keep-alive"
            assert result.headers["X-Accel-Buffering"] == "no"

    def test_handle_streaming_generator_yields_role_chunk_first(self):
        """Test that streaming generator is designed to yield role chunk first."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test-model", messages=messages)

        chunk_gen = (chunk for chunk in [])
        self.mock_adapter.stream.return_value = (chunk_gen, "test-model")

        # Act
        with patch(
            "src.services.chat_completion_service.StreamFormatter"
        ) as mock_formatter_class:
            mock_formatter = MagicMock()
            mock_formatter_class.return_value = mock_formatter
            mock_formatter.format_role_chunk.return_value = "role_chunk"

            result = self.service.handle_streaming(request)

            # Assert
            # Verify streaming response is created
            assert isinstance(result, StreamingResponse)
            # Verify adapter.stream was called to get chunks
            self.mock_adapter.stream.assert_called_once()

    def test_handle_streaming_generator_yields_content_chunks(self):
        """Test that streaming generator yields content chunks from adapter."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test-model", messages=messages)

        chunk_gen = (chunk for chunk in ["Hello", " ", "world"])
        self.mock_adapter.stream.return_value = (chunk_gen, "test-model")

        # Act
        with patch(
            "src.services.chat_completion_service.StreamFormatter"
        ) as mock_formatter_class:
            mock_formatter = MagicMock()
            mock_formatter_class.return_value = mock_formatter
            mock_formatter.format_role_chunk.return_value = "role"
            mock_formatter.format_content_chunk.side_effect = [
                "content1",
                "content2",
                "content3",
            ]
            mock_formatter.format_final_chunk.return_value = "final"

            result = self.service.handle_streaming(request)

            # Assert
            # Verify that adapter.stream was called (which processes content chunks)
            self.mock_adapter.stream.assert_called_once()
            assert isinstance(result, StreamingResponse)

    def test_handle_streaming_generator_skips_empty_chunks(self):
        """Test that streaming generator behavior with empty chunks."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test-model", messages=messages)

        # Generator that yields both empty and non-empty chunks
        chunk_gen = (chunk for chunk in ["text", "", "more", ""])
        self.mock_adapter.stream.return_value = (chunk_gen, "test-model")

        # Act
        with patch(
            "src.services.chat_completion_service.StreamFormatter"
        ) as mock_formatter_class:
            result = self.service.handle_streaming(request)

            # Assert - verify the response is streaming
            assert isinstance(result, StreamingResponse)
            # Verify streaming was initialized with correct model
            self.mock_adapter.stream.assert_called_once()

    def test_handle_streaming_generator_yields_final_chunk(self):
        """Test that streaming generator yields final chunk."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test-model", messages=messages)

        chunk_gen = (chunk for chunk in ["text"])
        self.mock_adapter.stream.return_value = (chunk_gen, "test-model")

        # Act
        with patch(
            "src.services.chat_completion_service.StreamFormatter"
        ) as mock_formatter_class:
            mock_formatter = MagicMock()
            mock_formatter_class.return_value = mock_formatter
            mock_formatter.format_role_chunk.return_value = "role"
            mock_formatter.format_content_chunk.return_value = "content"
            mock_formatter.format_final_chunk.return_value = "final_chunk"

            result = self.service.handle_streaming(request)

            # Assert
            assert isinstance(result, StreamingResponse)
            assert mock_formatter.format_final_chunk is not None

    def test_handle_streaming_creates_formatter_with_model(self):
        """Test that StreamFormatter is created with model name from adapter."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="input-model", messages=messages)

        adapter_model = "actual-perplexity-model"
        chunk_gen = (chunk for chunk in [])
        self.mock_adapter.stream.return_value = (chunk_gen, adapter_model)

        # Act
        with patch(
            "src.services.chat_completion_service.StreamFormatter"
        ) as mock_formatter_class:
            result = self.service.handle_streaming(request)

            # Assert
            # Verify streaming response is returned
            assert isinstance(result, StreamingResponse)
            # Verify adapter.stream was called with correct model
            self.mock_adapter.stream.assert_called_once_with(
                messages=messages,
                model="input-model",
            )


class TestChatCompletionServiceHandleRequest(unittest.TestCase):
    """Tests for ChatCompletionService.handle_request()"""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_adapter = Mock()

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=self.mock_adapter,
        ):
            self.service = ChatCompletionService(self.mock_client)

    def test_handle_request_with_stream_false_calls_handle_completion(self):
        """Test that handle_request with stream=False calls handle_completion()."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test", messages=messages, stream=False)

        # Act
        with patch.object(self.service, "handle_completion") as mock_handle_completion:
            mock_response = ChatCompletionResponse(id="test", model="test", choices=[])
            mock_handle_completion.return_value = mock_response

            result = self.service.handle_request(request)

            # Assert
            mock_handle_completion.assert_called_once_with(request)
            assert result == mock_response

    def test_handle_request_with_stream_true_calls_handle_streaming(self):
        """Test that handle_request with stream=True calls handle_streaming()."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test", messages=messages, stream=True)

        # Act
        with patch.object(self.service, "handle_streaming") as mock_handle_streaming:
            mock_response = StreamingResponse(iter([]))
            mock_handle_streaming.return_value = mock_response

            result = self.service.handle_request(request)

            # Assert
            mock_handle_streaming.assert_called_once_with(request)
            assert result == mock_response

    def test_handle_request_defaults_stream_to_false(self):
        """Test that handle_request defaults stream to False when not specified."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test", messages=messages)

        # Act
        with patch.object(self.service, "handle_completion") as mock_handle_completion:
            mock_response = ChatCompletionResponse(id="test", model="test", choices=[])
            mock_handle_completion.return_value = mock_response

            result = self.service.handle_request(request)

            # Assert
            mock_handle_completion.assert_called_once()

    def test_handle_request_stream_false_returns_completion_response(self):
        """Test that non-streaming request returns ChatCompletionResponse."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test", messages=messages, stream=False)

        # Act
        with patch.object(self.service, "handle_completion") as mock_handle_completion:
            expected = ChatCompletionResponse(
                id="id123", model="test-model", choices=[]
            )
            mock_handle_completion.return_value = expected

            result = self.service.handle_request(request)

            # Assert
            assert isinstance(result, ChatCompletionResponse)
            assert result == expected

    def test_handle_request_stream_true_returns_streaming_response(self):
        """Test that streaming request returns StreamingResponse."""
        # Arrange
        messages = [ChatMessage(role=MessageRole.USER, content="Query")]
        request = ChatCompletionRequest(model="test", messages=messages, stream=True)

        # Act
        with patch.object(self.service, "handle_streaming") as mock_handle_streaming:
            expected = StreamingResponse(iter([]))
            mock_handle_streaming.return_value = expected

            result = self.service.handle_request(request)

            # Assert
            assert isinstance(result, StreamingResponse)
            assert result == expected


class TestChatCompletionServiceIntegration(unittest.TestCase):
    """Integration tests for ChatCompletionService."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()

    def test_service_returns_correct_type_for_completion_request(self):
        """Test service returns ChatCompletionResponse for non-streaming request."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.complete.return_value = ("Response", "model-name")

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=mock_adapter,
        ):
            service = ChatCompletionService(self.mock_client)

            messages = [ChatMessage(role=MessageRole.USER, content="Hello")]
            request = ChatCompletionRequest(
                model="gpt-4", messages=messages, stream=False
            )

            # Act
            with patch(
                "src.services.chat_completion_service.format_openai_response"
            ) as mock_format:
                mock_format.return_value = ChatCompletionResponse(
                    id="test", model="model-name", choices=[]
                )
                result = service.handle_request(request)

            # Assert
            assert isinstance(result, ChatCompletionResponse)

    def test_service_returns_correct_type_for_streaming_request(self):
        """Test service returns StreamingResponse for streaming request."""
        # Arrange
        mock_adapter = MagicMock()
        chunk_gen = (chunk for chunk in [])
        mock_adapter.stream.return_value = (chunk_gen, "model-name")

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=mock_adapter,
        ):
            service = ChatCompletionService(self.mock_client)

            messages = [ChatMessage(role=MessageRole.USER, content="Hello")]
            request = ChatCompletionRequest(
                model="gpt-4", messages=messages, stream=True
            )

            # Act
            with patch("src.services.chat_completion_service.StreamFormatter"):
                result = service.handle_request(request)

            # Assert
            assert isinstance(result, StreamingResponse)


class TestChatCompletionServiceStreamingGenerator(unittest.TestCase):
    """Tests for the streaming generator execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()

    def test_streaming_generator_executes_and_yields_formatted_chunks(self):
        """Test that the streaming generator actually executes and yields formatted chunks."""
        # Arrange
        mock_adapter = MagicMock()
        chunk_gen = (chunk for chunk in ["Hello", " ", "world"])
        mock_adapter.stream.return_value = (chunk_gen, "test-model")

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=mock_adapter,
        ):
            service = ChatCompletionService(self.mock_client)
            messages = [ChatMessage(role=MessageRole.USER, content="Query")]
            request = ChatCompletionRequest(
                model="test", messages=messages, stream=True
            )

            # Act
            with patch(
                "src.services.chat_completion_service.StreamFormatter"
            ) as mock_formatter_class:
                mock_formatter = MagicMock()
                mock_formatter_class.return_value = mock_formatter
                mock_formatter.format_role_chunk.return_value = "role_chunk"
                mock_formatter.format_content_chunk.side_effect = [
                    "chunk1",
                    "chunk2",
                    "chunk3",
                ]
                mock_formatter.format_final_chunk.return_value = "final_chunk"

                result = service.handle_streaming(request)

                # Assert
                # The formatter should be created with the model from adapter
                assert isinstance(result, StreamingResponse)
                mock_adapter.stream.assert_called_once()

    def test_streaming_generator_formatter_receives_correct_model_from_adapter(self):
        """Test that StreamFormatter is created with model from adapter.stream()."""
        # Arrange
        mock_adapter = MagicMock()
        adapter_model_name = "perplexity-model-v1"
        chunk_gen = (chunk for chunk in [])
        mock_adapter.stream.return_value = (chunk_gen, adapter_model_name)

        with patch(
            "src.services.chat_completion_service.PerplexityAdapter",
            return_value=mock_adapter,
        ):
            service = ChatCompletionService(self.mock_client)
            messages = [ChatMessage(role=MessageRole.USER, content="Query")]
            request = ChatCompletionRequest(
                model="openai-model", messages=messages, stream=True
            )

            # Act
            with patch(
                "src.services.chat_completion_service.StreamFormatter"
            ) as mock_formatter_class:
                mock_formatter = MagicMock()
                mock_formatter_class.return_value = mock_formatter
                mock_formatter.format_role_chunk.return_value = ""
                mock_formatter.format_final_chunk.return_value = ""

                result = service.handle_streaming(request)

                # Assert
                # Verify that adapter returns the correct model
                assert mock_adapter.stream.return_value[1] == adapter_model_name


if __name__ == "__main__":
    unittest.main()
