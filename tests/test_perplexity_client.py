"""
Unit tests for src/core/perplexity_client.py

Tests cover:
- PerplexityClient initialization
- Cookie building
- Header building
- Payload building
- SSE line parsing
- PerplexityResponse dataclass
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from dataclasses import fields

from src.core.perplexity_client import PerplexityClient, PerplexityResponse


class TestPerplexityClientInit:
    """Tests for PerplexityClient.__init__()"""

    def test_init_loads_env_vars_successfully(self):
        """Test that __init__ loads all required environment variables."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
            "PERPLEXITY_SESSION_ID": "test_session_id",
            "PERPLEXITY_CF_BM": "test_cf_bm",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                client = PerplexityClient()

                assert client.session_token == "test_session_token"
                assert client.cf_clearance == "test_cf_clearance"
                assert client.visitor_id == "test_visitor_id"
                assert client.session_id == "test_session_id"
                assert client.cf_bm == "test_cf_bm"

    def test_init_raises_error_if_session_token_missing(self):
        """Test that ValueError is raised if PERPLEXITY_SESSION_TOKEN is missing."""
        env_vars = {
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                with pytest.raises(ValueError) as exc_info:
                    PerplexityClient()

                assert "PERPLEXITY_SESSION_TOKEN" in str(exc_info.value)

    def test_init_raises_error_if_cf_clearance_missing(self):
        """Test that ValueError is raised if PERPLEXITY_CF_CLEARANCE is missing."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                with pytest.raises(ValueError) as exc_info:
                    PerplexityClient()

                assert "PERPLEXITY_CF_CLEARANCE" in str(exc_info.value)

    def test_init_raises_error_if_visitor_id_missing(self):
        """Test that ValueError is raised if PERPLEXITY_VISITOR_ID is missing."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                with pytest.raises(ValueError) as exc_info:
                    PerplexityClient()

                assert "PERPLEXITY_VISITOR_ID" in str(exc_info.value)

    def test_init_allows_optional_session_id(self):
        """Test that PERPLEXITY_SESSION_ID is optional."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                client = PerplexityClient()
                assert client.session_id is None

    def test_init_allows_optional_cf_bm(self):
        """Test that PERPLEXITY_CF_BM is optional."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                client = PerplexityClient()
                assert client.cf_bm is None

    def test_init_loads_custom_env_path(self):
        """Test that custom env_path is passed to load_dotenv."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv") as mock_load:
                PerplexityClient(env_path="/custom/.env")
                mock_load.assert_called_once_with("/custom/.env")

    def test_init_loads_default_env_path(self):
        """Test that load_dotenv is called without path by default."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv") as mock_load:
                PerplexityClient()
                mock_load.assert_called_once_with()


class TestBuildCookies:
    """Tests for PerplexityClient._build_cookies()"""

    def _create_client(self, **kwargs):
        """Helper to create a client with mocked env vars."""
        defaults = {
            "session_token": "test_session_token",
            "cf_clearance": "test_cf_clearance",
            "visitor_id": "test_visitor_id",
            "session_id": None,
            "cf_bm": None,
        }
        defaults.update(kwargs)

        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": defaults["session_token"],
            "PERPLEXITY_CF_CLEARANCE": defaults["cf_clearance"],
            "PERPLEXITY_VISITOR_ID": defaults["visitor_id"],
        }
        if defaults["session_id"]:
            env_vars["PERPLEXITY_SESSION_ID"] = defaults["session_id"]
        if defaults["cf_bm"]:
            env_vars["PERPLEXITY_CF_BM"] = defaults["cf_bm"]

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                return PerplexityClient()

    def test_build_cookies_includes_required_cookies(self):
        """Test that _build_cookies includes all required cookies."""
        client = self._create_client()
        cookies = client._build_cookies()

        assert "pplx.visitor-id" in cookies
        assert "__Secure-next-auth.session-token" in cookies
        assert "cf_clearance" in cookies
        assert cookies["pplx.visitor-id"] == "test_visitor_id"
        assert cookies["__Secure-next-auth.session-token"] == "test_session_token"
        assert cookies["cf_clearance"] == "test_cf_clearance"

    def test_build_cookies_includes_optional_session_id(self):
        """Test that _build_cookies includes optional PERPLEXITY_SESSION_ID."""
        client = self._create_client(session_id="test_session_id")
        cookies = client._build_cookies()

        assert "pplx.session-id" in cookies
        assert cookies["pplx.session-id"] == "test_session_id"

    def test_build_cookies_filters_out_none_session_id(self):
        """Test that _build_cookies filters out None session_id."""
        client = self._create_client(session_id=None)
        cookies = client._build_cookies()

        assert "pplx.session-id" not in cookies

    def test_build_cookies_includes_optional_cf_bm(self):
        """Test that _build_cookies includes optional PERPLEXITY_CF_BM."""
        client = self._create_client(cf_bm="test_cf_bm")
        cookies = client._build_cookies()

        assert "__cf_bm" in cookies
        assert cookies["__cf_bm"] == "test_cf_bm"

    def test_build_cookies_filters_out_none_cf_bm(self):
        """Test that _build_cookies filters out None cf_bm."""
        client = self._create_client(cf_bm=None)
        cookies = client._build_cookies()

        assert "__cf_bm" not in cookies

    def test_build_cookies_filters_all_none_values(self):
        """Test that _build_cookies only returns non-None values."""
        client = self._create_client(session_id=None, cf_bm=None)
        cookies = client._build_cookies()

        # Only required cookies should be present
        assert len(cookies) == 3
        assert all(v is not None for v in cookies.values())

    def test_build_cookies_returns_dict(self):
        """Test that _build_cookies returns a dict."""
        client = self._create_client()
        cookies = client._build_cookies()

        assert isinstance(cookies, dict)


class TestBuildHeaders:
    """Tests for PerplexityClient._build_headers()"""

    def _create_client(self):
        """Helper to create a client with mocked env vars."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                return PerplexityClient()

    def test_build_headers_returns_dict(self):
        """Test that _build_headers returns a dict."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert isinstance(headers, dict)

    def test_build_headers_includes_accept(self):
        """Test that _build_headers includes accept header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "accept" in headers
        assert headers["accept"] == "text/event-stream"

    def test_build_headers_includes_accept_language(self):
        """Test that _build_headers includes accept-language header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "accept-language" in headers
        assert headers["accept-language"] == "en-US,en;q=0.9"

    def test_build_headers_includes_content_type(self):
        """Test that _build_headers includes content-type header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "content-type" in headers
        assert headers["content-type"] == "application/json"

    def test_build_headers_includes_origin(self):
        """Test that _build_headers includes origin header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "origin" in headers
        assert headers["origin"] == "https://www.perplexity.ai"

    def test_build_headers_includes_referer(self):
        """Test that _build_headers includes referer header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "referer" in headers
        assert headers["referer"] == "https://www.perplexity.ai/?"

    def test_build_headers_includes_user_agent(self):
        """Test that _build_headers includes user-agent header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "user-agent" in headers
        assert "Mozilla" in headers["user-agent"]

    def test_build_headers_includes_x_request_id(self):
        """Test that _build_headers includes x-request-id header."""
        client = self._create_client()
        request_id = "test-request-id-123"
        headers = client._build_headers(request_id)

        assert "x-request-id" in headers
        assert headers["x-request-id"] == request_id

    def test_build_headers_x_request_id_matches_input(self):
        """Test that x-request-id matches the provided request_id."""
        client = self._create_client()

        request_id_1 = "request-id-001"
        headers_1 = client._build_headers(request_id_1)
        assert headers_1["x-request-id"] == request_id_1

        request_id_2 = "request-id-002"
        headers_2 = client._build_headers(request_id_2)
        assert headers_2["x-request-id"] == request_id_2

    def test_build_headers_includes_sec_ch_ua(self):
        """Test that _build_headers includes sec-ch-ua header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "sec-ch-ua" in headers

    def test_build_headers_includes_x_perplexity_request_reason(self):
        """Test that _build_headers includes x-perplexity-request-reason header."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        assert "x-perplexity-request-reason" in headers

    def test_build_headers_all_values_are_strings(self):
        """Test that all header values are strings."""
        client = self._create_client()
        headers = client._build_headers("test-request-id")

        for key, value in headers.items():
            assert isinstance(value, str), (
                f"Header {key} value is not a string: {value}"
            )


class TestBuildPayload:
    """Tests for PerplexityClient._build_payload()"""

    def _create_client(self):
        """Helper to create a client with mocked env vars."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                return PerplexityClient()

    def test_build_payload_returns_dict(self):
        """Test that _build_payload returns a dict."""
        client = self._create_client()
        payload = client._build_payload("test query")

        assert isinstance(payload, dict)

    def test_build_payload_includes_query_str(self):
        """Test that _build_payload includes query_str."""
        client = self._create_client()
        query = "what is python"
        payload = client._build_payload(query)

        assert "query_str" in payload
        assert payload["query_str"] == query

    def test_build_payload_includes_params(self):
        """Test that _build_payload includes params dict."""
        client = self._create_client()
        payload = client._build_payload("test query")

        assert "params" in payload
        assert isinstance(payload["params"], dict)

    def test_build_payload_params_includes_dsl_query(self):
        """Test that params includes dsl_query."""
        client = self._create_client()
        query = "test query"
        payload = client._build_payload(query)

        assert "dsl_query" in payload["params"]
        assert payload["params"]["dsl_query"] == query

    def test_build_payload_params_includes_mode(self):
        """Test that params includes mode."""
        client = self._create_client()
        payload = client._build_payload("test", mode="search")

        assert "mode" in payload["params"]
        assert payload["params"]["mode"] == "search"

    def test_build_payload_mode_defaults_to_copilot(self):
        """Test that mode defaults to copilot."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["mode"] == "copilot"

    def test_build_payload_params_includes_model_preference(self):
        """Test that params includes model_preference."""
        client = self._create_client()
        payload = client._build_payload("test", model_preference="gpt-4")

        assert "model_preference" in payload["params"]
        assert payload["params"]["model_preference"] == "gpt-4"

    def test_build_payload_model_preference_defaults_correctly(self):
        """Test that model_preference defaults correctly."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["model_preference"] == "claude45sonnetthinking"

    def test_build_payload_params_includes_search_focus(self):
        """Test that params includes search_focus."""
        client = self._create_client()
        payload = client._build_payload("test", search_focus="academic")

        assert "search_focus" in payload["params"]
        assert payload["params"]["search_focus"] == "academic"

    def test_build_payload_search_focus_defaults_to_internet(self):
        """Test that search_focus defaults to internet."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["search_focus"] == "internet"

    def test_build_payload_params_includes_language(self):
        """Test that params includes language."""
        client = self._create_client()
        payload = client._build_payload("test", language="fr-FR")

        assert "language" in payload["params"]
        assert payload["params"]["language"] == "fr-FR"

    def test_build_payload_language_defaults_to_en_us(self):
        """Test that language defaults to en-US."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["language"] == "en-US"

    def test_build_payload_params_includes_timezone(self):
        """Test that params includes timezone."""
        client = self._create_client()
        payload = client._build_payload("test", timezone="UTC")

        assert "timezone" in payload["params"]
        assert payload["params"]["timezone"] == "UTC"

    def test_build_payload_timezone_defaults_correctly(self):
        """Test that timezone defaults correctly."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["timezone"] == "Asia/Bangkok"

    def test_build_payload_params_includes_sources(self):
        """Test that params includes sources."""
        client = self._create_client()
        sources = ["web", "scholar"]
        payload = client._build_payload("test", sources=sources)

        assert "sources" in payload["params"]
        assert payload["params"]["sources"] == sources

    def test_build_payload_sources_defaults_correctly(self):
        """Test that sources defaults correctly."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["sources"] == ["web", "scholar"]

    def test_build_payload_params_includes_is_incognito(self):
        """Test that params includes is_incognito."""
        client = self._create_client()
        payload = client._build_payload("test", is_incognito=True)

        assert "is_incognito" in payload["params"]
        assert payload["params"]["is_incognito"] is True

    def test_build_payload_is_incognito_defaults_to_false(self):
        """Test that is_incognito defaults to False."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["is_incognito"] is False

    def test_build_payload_generates_unique_uuids(self):
        """Test that _build_payload generates unique UUIDs."""
        client = self._create_client()
        payload1 = client._build_payload("test")
        payload2 = client._build_payload("test")

        frontend_uuid_1 = payload1["params"]["frontend_uuid"]
        frontend_uuid_2 = payload2["params"]["frontend_uuid"]

        assert frontend_uuid_1 != frontend_uuid_2

    def test_build_payload_includes_frontend_uuid(self):
        """Test that params includes frontend_uuid."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert "frontend_uuid" in payload["params"]
        # UUID format check: 8-4-4-4-12 hex digits
        uuid_str = payload["params"]["frontend_uuid"]
        assert len(uuid_str) == 36  # Standard UUID length
        assert uuid_str.count("-") == 4

    def test_build_payload_includes_frontend_context_uuid(self):
        """Test that params includes frontend_context_uuid."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert "frontend_context_uuid" in payload["params"]
        uuid_str = payload["params"]["frontend_context_uuid"]
        assert len(uuid_str) == 36

    def test_build_payload_includes_required_params(self):
        """Test that payload includes all required params."""
        client = self._create_client()
        payload = client._build_payload("test")
        params = payload["params"]

        required_keys = [
            "attachments",
            "language",
            "timezone",
            "search_focus",
            "sources",
            "frontend_uuid",
            "mode",
            "model_preference",
            "is_incognito",
            "dsl_query",
            "version",
        ]

        for key in required_keys:
            assert key in params, f"Missing required param: {key}"

    def test_build_payload_attachments_is_empty_list(self):
        """Test that attachments is an empty list."""
        client = self._create_client()
        payload = client._build_payload("test")

        assert payload["params"]["attachments"] == []


class TestParseSSELine:
    """Tests for PerplexityClient._parse_sse_line()"""

    def _create_client(self):
        """Helper to create a client with mocked env vars."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                return PerplexityClient()

    def test_parse_sse_line_parses_valid_data_line(self):
        """Test that _parse_sse_line parses valid 'data: {...}' lines."""
        client = self._create_client()
        data = {"key": "value", "nested": {"inner": "data"}}
        line = f"data: {json.dumps(data)}"

        result = client._parse_sse_line(line)

        assert result == data

    def test_parse_sse_line_returns_none_for_empty_line(self):
        """Test that _parse_sse_line returns None for empty lines."""
        client = self._create_client()

        result = client._parse_sse_line("")

        assert result is None

    def test_parse_sse_line_returns_none_for_whitespace_line(self):
        """Test that _parse_sse_line returns None for whitespace-only lines."""
        client = self._create_client()

        result = client._parse_sse_line("   ")

        assert result is None

    def test_parse_sse_line_returns_none_for_non_data_line(self):
        """Test that _parse_sse_line returns None for non-data lines."""
        client = self._create_client()

        result = client._parse_sse_line("event: message")

        assert result is None

    def test_parse_sse_line_returns_none_for_invalid_json(self):
        """Test that _parse_sse_line returns None for invalid JSON."""
        client = self._create_client()

        result = client._parse_sse_line("data: {invalid json}")

        assert result is None

    def test_parse_sse_line_returns_none_for_data_with_empty_content(self):
        """Test that _parse_sse_line returns None for 'data:' with no content."""
        client = self._create_client()

        result = client._parse_sse_line("data:")

        assert result is None

    def test_parse_sse_line_returns_none_for_data_with_only_whitespace(self):
        """Test that _parse_sse_line returns None for 'data:   ' (whitespace only)."""
        client = self._create_client()

        result = client._parse_sse_line("data:   ")

        assert result is None

    def test_parse_sse_line_parses_complex_json(self):
        """Test that _parse_sse_line parses complex JSON structures."""
        client = self._create_client()
        data = {
            "step_type": "FINAL",
            "text": '{"nested": "json"}',
            "citations": [{"title": "Example", "url": "https://example.com"}],
            "related_queries": ["query1", "query2"],
        }
        line = f"data: {json.dumps(data)}"

        result = client._parse_sse_line(line)

        assert result == data
        assert result["step_type"] == "FINAL"
        assert isinstance(result["citations"], list)

    def test_parse_sse_line_parses_with_extra_whitespace(self):
        """Test that _parse_sse_line handles extra whitespace correctly."""
        client = self._create_client()
        data = {"key": "value"}
        line = f"data:   {json.dumps(data)}   "

        result = client._parse_sse_line(line)

        assert result == data

    def test_parse_sse_line_strips_data_content(self):
        """Test that _parse_sse_line strips the data content correctly."""
        client = self._create_client()
        data = {"test": "data"}
        # Note: line itself should not have leading whitespace, only the data content
        line = f"data: {json.dumps(data)}  "

        result = client._parse_sse_line(line)

        assert result == data

    def test_parse_sse_line_parses_null_json(self):
        """Test that _parse_sse_line handles null JSON."""
        client = self._create_client()
        line = "data: null"

        result = client._parse_sse_line(line)

        assert result is None

    def test_parse_sse_line_parses_array_json(self):
        """Test that _parse_sse_line can parse JSON arrays."""
        client = self._create_client()
        data = [1, 2, 3, {"key": "value"}]
        line = f"data: {json.dumps(data)}"

        result = client._parse_sse_line(line)

        assert result == data
        assert isinstance(result, list)

    def test_parse_sse_line_parses_string_json(self):
        """Test that _parse_sse_line can parse JSON strings."""
        client = self._create_client()
        line = 'data: "just a string"'

        result = client._parse_sse_line(line)

        assert result == "just a string"

    def test_parse_sse_line_parses_number_json(self):
        """Test that _parse_sse_line can parse JSON numbers."""
        client = self._create_client()
        line = "data: 42"

        result = client._parse_sse_line(line)

        assert result == 42

    def test_parse_sse_line_parses_boolean_json(self):
        """Test that _parse_sse_line can parse JSON booleans."""
        client = self._create_client()

        result_true = client._parse_sse_line("data: true")
        result_false = client._parse_sse_line("data: false")

        assert result_true is True
        assert result_false is False


class TestPerplexityResponse:
    """Tests for PerplexityResponse dataclass"""

    def test_response_has_text_field(self):
        """Test that PerplexityResponse has a text field."""
        response = PerplexityResponse()

        assert hasattr(response, "text")
        assert response.text == ""

    def test_response_has_citations_field(self):
        """Test that PerplexityResponse has a citations field."""
        response = PerplexityResponse()

        assert hasattr(response, "citations")
        assert response.citations == []

    def test_response_has_media_items_field(self):
        """Test that PerplexityResponse has a media_items field."""
        response = PerplexityResponse()

        assert hasattr(response, "media_items")
        assert response.media_items == []

    def test_response_has_related_queries_field(self):
        """Test that PerplexityResponse has a related_queries field."""
        response = PerplexityResponse()

        assert hasattr(response, "related_queries")
        assert response.related_queries == []

    def test_response_has_raw_events_field(self):
        """Test that PerplexityResponse has a raw_events field."""
        response = PerplexityResponse()

        assert hasattr(response, "raw_events")
        assert response.raw_events == []

    def test_response_text_default_is_empty_string(self):
        """Test that text defaults to empty string."""
        response = PerplexityResponse()

        assert isinstance(response.text, str)
        assert response.text == ""

    def test_response_citations_default_is_empty_list(self):
        """Test that citations defaults to empty list."""
        response = PerplexityResponse()

        assert isinstance(response.citations, list)
        assert len(response.citations) == 0

    def test_response_media_items_default_is_empty_list(self):
        """Test that media_items defaults to empty list."""
        response = PerplexityResponse()

        assert isinstance(response.media_items, list)
        assert len(response.media_items) == 0

    def test_response_related_queries_default_is_empty_list(self):
        """Test that related_queries defaults to empty list."""
        response = PerplexityResponse()

        assert isinstance(response.related_queries, list)
        assert len(response.related_queries) == 0

    def test_response_raw_events_default_is_empty_list(self):
        """Test that raw_events defaults to empty list."""
        response = PerplexityResponse()

        assert isinstance(response.raw_events, list)
        assert len(response.raw_events) == 0

    def test_response_can_set_text(self):
        """Test that text can be set."""
        response = PerplexityResponse(text="Hello, world!")

        assert response.text == "Hello, world!"

    def test_response_can_set_citations(self):
        """Test that citations can be set."""
        citations = [{"title": "Example", "url": "https://example.com"}]
        response = PerplexityResponse(citations=citations)

        assert response.citations == citations

    def test_response_can_set_media_items(self):
        """Test that media_items can be set."""
        media_items = [{"type": "image", "url": "https://example.com/image.jpg"}]
        response = PerplexityResponse(media_items=media_items)

        assert response.media_items == media_items

    def test_response_can_set_related_queries(self):
        """Test that related_queries can be set."""
        related_queries = ["query1", "query2"]
        response = PerplexityResponse(related_queries=related_queries)

        assert response.related_queries == related_queries

    def test_response_can_set_raw_events(self):
        """Test that raw_events can be set."""
        raw_events = [{"event": "data"}]
        response = PerplexityResponse(raw_events=raw_events)

        assert response.raw_events == raw_events

    def test_response_is_dataclass(self):
        """Test that PerplexityResponse is a dataclass."""
        response = PerplexityResponse()

        # Check that it has dataclass fields
        assert hasattr(PerplexityResponse, "__dataclass_fields__")

    def test_response_has_all_expected_fields(self):
        """Test that PerplexityResponse has all expected fields."""
        response = PerplexityResponse()
        field_names = {f.name for f in fields(PerplexityResponse)}

        expected_fields = {
            "text",
            "citations",
            "media_items",
            "related_queries",
            "raw_events",
        }

        assert field_names == expected_fields

    def test_response_lists_are_independent(self):
        """Test that list fields are independent between instances."""
        response1 = PerplexityResponse()
        response2 = PerplexityResponse()

        response1.citations.append({"title": "Test"})

        assert len(response1.citations) == 1
        assert len(response2.citations) == 0


# Integration test helpers (not full integration, but testing method interactions)
class TestPerplexityClientIntegration:
    """Tests for interactions between PerplexityClient methods"""

    def _create_client(self):
        """Helper to create a client with mocked env vars."""
        env_vars = {
            "PERPLEXITY_SESSION_TOKEN": "test_session_token",
            "PERPLEXITY_CF_CLEARANCE": "test_cf_clearance",
            "PERPLEXITY_VISITOR_ID": "test_visitor_id",
            "PERPLEXITY_SESSION_ID": "test_session_id",
            "PERPLEXITY_CF_BM": "test_cf_bm",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.core.perplexity_client.load_dotenv"):
                return PerplexityClient()

    def test_client_methods_work_together(self):
        """Test that build methods work together without errors."""
        client = self._create_client()

        cookies = client._build_cookies()
        headers = client._build_headers("test-id")
        payload = client._build_payload("test query")

        assert isinstance(cookies, dict)
        assert isinstance(headers, dict)
        assert isinstance(payload, dict)

        assert len(cookies) > 0
        assert len(headers) > 0
        assert "params" in payload

    def test_cookies_contains_no_none_values(self):
        """Test that _build_cookies never contains None values."""
        client = self._create_client()
        cookies = client._build_cookies()

        for key, value in cookies.items():
            assert value is not None, f"Cookie {key} contains None"

    def test_headers_contains_no_none_values(self):
        """Test that _build_headers never contains None values."""
        client = self._create_client()
        headers = client._build_headers("test-id")

        for key, value in headers.items():
            assert value is not None, f"Header {key} contains None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
