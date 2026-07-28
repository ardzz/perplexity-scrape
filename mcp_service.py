"""
Perplexity MCP Server

An MCP server that provides Perplexity AI search capabilities.
"""

import logging
import os
from typing import Literal, Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from src.core.perplexity_client import PerplexityClient
from src.prompts import PROGRAMMING_RESEARCH_PROMPTS, VALID_CATEGORIES

logger = logging.getLogger(__name__)


def get_transport_security() -> TransportSecuritySettings:
    """Configure MCP transport security settings.

    By default, DNS rebinding protection is DISABLED for ease of deployment
    behind reverse proxies. Set MCP_ENABLE_HOST_CHECK=true to enable it.

    When enabled, use MCP_ALLOWED_HOSTS to specify allowed domains (comma-separated).
    Example: MCP_ALLOWED_HOSTS=api.example.com,myapp.sslip.io

    Environment variables:
        MCP_ENABLE_HOST_CHECK: Set to 'true' to enable host validation (default: false)
        MCP_ALLOWED_HOSTS: Comma-separated list of allowed hosts (only when check enabled)
    """
    enable_check = os.environ.get("MCP_ENABLE_HOST_CHECK", "").lower() in (
        "true",
        "1",
        "yes",
    )

    if not enable_check:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)

    allowed_hosts = [
        "localhost",
        "localhost:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "0.0.0.0",
        "0.0.0.0:*",
    ]

    custom_hosts = os.environ.get("MCP_ALLOWED_HOSTS", "")
    if custom_hosts:
        allowed_hosts.extend([h.strip() for h in custom_hosts.split(",") if h.strip()])

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
    )


transport_security = get_transport_security()

mcp = FastMCP("Perplexity Search", transport_security=transport_security)
_client: Optional[PerplexityClient] = None

DEFAULT_MODEL = "gpt56_terra_thinking"

ResearchCategory = Literal[
    "academic",
    "api",
    "library",
    "implementation",
    "debugging",
    "comparison",
    "general",
    "ml_architecture",
    "ml_training",
    "ml_concepts",
    "ml_frameworks",
    "ml_math",
    "ml_paper",
    "ml_debugging",
    "ml_dataset_tabular",
    "ml_dataset_image",
    "ml_dataset_text",
    "ml_dataset_timeseries",
    "ml_dataset_audio",
    "ml_dataset_graph",
    "ml_dataset_multimodal",
]


def get_client() -> PerplexityClient:
    """Get or create the Perplexity client."""
    global _client
    if _client is None:
        _client = PerplexityClient()
    return _client


def _build_response(
    response,
    include_citations: bool,
    include_related: bool,
) -> dict:
    """Build a response dict including only requested optional fields."""
    result: dict = {"text": response.text or "No response received."}
    if include_citations:
        result["citations"] = response.citations
    if include_related:
        result["related_queries"] = response.related_queries
    return result


def _error_dict(error: Exception) -> dict:
    """Build an error response with minimal shape."""
    msg = f"[Error] {type(error).__name__}: {error}"
    logger.error(msg)
    return {"text": msg}


@mcp.tool()
def perplexity_search(
    query: str,
    sources: Optional[list[Literal["web", "scholar"]]] = None,
    include_citations: bool = False,
    include_related: bool = False,
    model_preference: str = DEFAULT_MODEL,
    mode: Literal["copilot", "search"] = "copilot",
) -> dict:
    """Search via Perplexity AI. Returns answer text; citations opt-in.

    Args:
        query: The search query.
        sources: Search sources. Use ["web"] (default), ["scholar"] for academic,
            or ["web", "scholar"] for combined results.
        include_citations: If True, include source citations in response.
            Default False to save tokens.
        include_related: If True, include related query suggestions.
        model_preference: AI model to use.
        mode: "copilot" for comprehensive answers, "search" for quick results.

    Returns:
        Dict with "text" always present. "citations" and "related_queries"
        included only when their respective flags are True.
    """
    selected_sources: list[str] = list(sources) if sources else ["web"]
    search_focus = "academic" if selected_sources == ["scholar"] else "internet"

    try:
        client = get_client()
        response = client.ask(
            query=query,
            mode=mode,
            model_preference=model_preference,
            search_focus=search_focus,
            sources=selected_sources,
        )
        return _build_response(response, include_citations, include_related)
    except Exception as e:
        return _error_dict(e)


@mcp.tool()
def perplexity_research(
    topic: str,
    category: ResearchCategory = "general",
    include_citations: bool = False,
    include_related: bool = False,
    model_preference: str = DEFAULT_MODEL,
) -> dict:
    """Research a topic with category-specific prompts. Citations opt-in.

    Args:
        topic: The topic to research.
        category: Research category determining the prompt template.
            Use "academic" for non-programming topics, "general" for
            programming-focused research, "api"/"library"/"implementation"/
            "debugging"/"comparison" for targeted programming research, or
            an "ml_*" category for machine-learning research.
        include_citations: If True, include source citations. Default False.
        include_related: If True, include related query suggestions.
        model_preference: AI model to use.

    Returns:
        Dict with "text" always present. "citations" and "related_queries"
        included only when their respective flags are True.
    """
    normalized_category = category.lower().strip()
    if normalized_category not in VALID_CATEGORIES:
        normalized_category = "general"

    prompt_template = PROGRAMMING_RESEARCH_PROMPTS[normalized_category]
    research_prompt = prompt_template.format(topic=topic)

    try:
        client = get_client()
        response = client.ask(
            query=research_prompt,
            mode="copilot",
            model_preference=model_preference,
            search_focus="internet",
            sources=["web", "scholar"],
        )
        return _build_response(response, include_citations, include_related)
    except Exception as e:
        return _error_dict(e)


if __name__ == "__main__":
    from src.config import config

    if config.mcp_transport_mode == "http":
        import uvicorn
        from src.core.mcp_auth import MCPAuthMiddleware

        app = mcp.streamable_http_app()
        app.add_middleware(MCPAuthMiddleware)

        uvicorn.run(
            app,
            host=config.mcp_http_host,
            port=config.mcp_http_port,
        )
    else:
        mcp.run()
