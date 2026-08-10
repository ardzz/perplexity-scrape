"""Tests for the MCP tool surface (perplexity_search & perplexity_research).

These unit tests mock PerplexityClient to avoid live API calls. They verify:
- Response shape defaults to {"text": ...} (no citations/related_queries)
- include_citations=True adds "citations"
- include_related=True adds "related_queries"
- Sources routing (web/scholar) maps to correct search_focus
- Research category validation & "academic" category resolves
- Error responses return {"text": "[Error] ..."}
"""

from unittest.mock import MagicMock, patch

import pytest

import mcp_service


@pytest.fixture
def mock_response():
    """Build a fake PerplexityResponse-like object."""
    resp = MagicMock()
    resp.text = "The answer is 42."
    resp.citations = [
        {"title": "Source A", "url": "https://a.example", "snippet": "snippet a"},
        {"title": "Source B", "url": "https://b.example", "snippet": "snippet b"},
    ]
    resp.related_queries = ["query 1", "query 2"]
    resp.partial = False
    resp.warning = None
    return resp


@pytest.fixture
def mock_client(mock_response):
    """Patch get_client() to return a mock whose .ask() returns mock_response."""
    client = MagicMock()
    client.ask.return_value = mock_response
    with patch.object(mcp_service, "get_client", return_value=client):
        # Also reset the module-level cached client
        mcp_service._client = None
        yield client


class TestPerplexitySearchResponseShape:
    """Verify conditional response shape for perplexity_search."""

    def test_default_returns_text_only(self, mock_client):
        result = mcp_service.perplexity_search("hello")
        assert result == {"text": "The answer is 42."}
        assert "citations" not in result
        assert "related_queries" not in result
        assert "media_count" not in result

    def test_include_citations_adds_citations(self, mock_client):
        result = mcp_service.perplexity_search("hello", include_citations=True)
        assert "citations" in result
        assert len(result["citations"]) == 2
        assert "related_queries" not in result

    def test_include_related_adds_related_queries(self, mock_client):
        result = mcp_service.perplexity_search("hello", include_related=True)
        assert "related_queries" in result
        assert result["related_queries"] == ["query 1", "query 2"]
        assert "citations" not in result

    def test_both_flags_include_both(self, mock_client):
        result = mcp_service.perplexity_search(
            "hello", include_citations=True, include_related=True
        )
        assert "citations" in result
        assert "related_queries" in result
        assert "text" in result


class TestPerplexitySearchSourcesRouting:
    """Verify sources parameter maps to the right search_focus."""

    def test_default_sources_web(self, mock_client):
        mcp_service.perplexity_search("q")
        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["sources"] == ["web"]
        assert call_kwargs["search_focus"] == "internet"
        assert call_kwargs["mode"] == "search"
        assert call_kwargs["model_preference"] == "gpt56_terra_thinking"
        assert call_kwargs["timeout_seconds"] == 45

    def test_scholar_only_uses_academic_focus(self, mock_client):
        mcp_service.perplexity_search("q", sources=["scholar"])
        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["sources"] == ["scholar"]
        assert call_kwargs["search_focus"] == "academic"

    def test_combined_sources_uses_internet_focus(self, mock_client):
        mcp_service.perplexity_search("q", sources=["web", "scholar"])
        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["sources"] == ["web", "scholar"]
        assert call_kwargs["search_focus"] == "internet"


class TestPerplexityResearch:
    """Verify perplexity_research tool."""

    def test_default_returns_text_only(self, mock_client):
        result = mcp_service.perplexity_research("topic X")
        assert "text" in result
        assert "citations" not in result
        assert "related_queries" not in result
        call_kwargs = mock_client.ask.call_args.kwargs
        assert call_kwargs["mode"] == "copilot"
        assert call_kwargs["timeout_seconds"] == 180

    def test_academic_category_resolves(self, mock_client):
        """New 'academic' category must be registered and load the academic template."""
        mcp_service.perplexity_research("topic", category="academic")
        call_kwargs = mock_client.ask.call_args.kwargs
        prompt = call_kwargs["query"]
        assert "academic/general context" in prompt
        assert "topic" in prompt

    def test_unknown_category_falls_back_to_general(self, mock_client):
        """Unknown category should silently fall back to 'general' template."""
        mcp_service.perplexity_research("topic", category="not_a_real_category")
        call_kwargs = mock_client.ask.call_args.kwargs
        # general.py TEMPLATE should contain a recognizable marker
        assert "topic" in call_kwargs["query"]

    def test_ml_dataset_category_uses_correct_template(self, mock_client):
        mcp_service.perplexity_research("housing", category="ml_dataset_tabular")
        call_kwargs = mock_client.ask.call_args.kwargs
        assert "tabular" in call_kwargs["query"].lower()
        assert "housing" in call_kwargs["query"]

    def test_include_citations_opt_in(self, mock_client):
        result = mcp_service.perplexity_research(
            "topic", category="general", include_citations=True
        )
        assert "citations" in result


class TestTimeoutAndPartialResponse:
    """Verify user-facing timeout controls and partial-result metadata."""

    @pytest.mark.parametrize("timeout_seconds", [4, 601])
    def test_search_rejects_timeout_outside_safe_range(self, timeout_seconds):
        result = mcp_service.perplexity_search("q", timeout_seconds=timeout_seconds)

        assert set(result) == {"text"}
        assert result["text"].startswith("[Error] ValueError:")
        assert "between 5 and 600" in result["text"]

    def test_custom_search_timeout_is_forwarded(self, mock_client):
        mcp_service.perplexity_search("q", timeout_seconds=30)

        assert mock_client.ask.call_args.kwargs["timeout_seconds"] == 30

    def test_partial_response_is_marked(self, mock_client, mock_response):
        mock_response.partial = True
        mock_response.warning = "Timed out after 45 seconds; returning partial answer."

        result = mcp_service.perplexity_search("q")

        assert result == {
            "text": "The answer is 42.",
            "partial": True,
            "warning": "Timed out after 45 seconds; returning partial answer.",
        }

    def test_empty_response_is_an_explicit_error(self, mock_client, mock_response):
        mock_response.text = ""

        result = mcp_service.perplexity_search("q")

        assert set(result) == {"text"}
        assert result["text"].startswith("[Error] EmptyResponseError:")


class TestErrorShape:
    """Error responses still match the minimal shape."""

    def test_search_error_returns_text_only(self):
        broken_client = MagicMock()
        broken_client.ask.side_effect = RuntimeError("boom")
        with patch.object(mcp_service, "get_client", return_value=broken_client):
            mcp_service._client = None
            result = mcp_service.perplexity_search("q")
        assert list(result.keys()) == ["text"]
        assert "[Error]" in result["text"]
        assert "boom" in result["text"]

    def test_research_error_returns_text_only(self):
        broken_client = MagicMock()
        broken_client.ask.side_effect = ValueError("nope")
        with patch.object(mcp_service, "get_client", return_value=broken_client):
            mcp_service._client = None
            result = mcp_service.perplexity_research("t")
        assert list(result.keys()) == ["text"]
        assert "[Error]" in result["text"]


class TestToolSurface:
    """Ensure only the 2 new tools are exposed, old tools are gone."""

    def test_old_tools_removed(self):
        removed = [
            "perplexity_ask",
            "perplexity_quick_search",
            "perplexity_academic_search",
            "perplexity_comprehensive_search",
            "perplexity_general_research",
        ]
        for name in removed:
            assert not hasattr(mcp_service, name), f"Old tool {name} should be removed"

    def test_new_tools_present(self):
        assert hasattr(mcp_service, "perplexity_search")
        assert hasattr(mcp_service, "perplexity_research")

    def test_fastmcp_schema_exposes_latency_defaults(self):
        """OpenCode must see the intended mode/model/timeout tool defaults."""
        tools = {tool.name: tool for tool in mcp_service.mcp._tool_manager.list_tools()}
        search = tools["perplexity_search"].parameters["properties"]
        research = tools["perplexity_research"].parameters["properties"]

        assert search["model_preference"]["default"] == "gpt56_terra_thinking"
        assert search["mode"]["default"] == "search"
        assert search["timeout_seconds"]["default"] == 45.0
        assert research["timeout_seconds"]["default"] == 180.0
