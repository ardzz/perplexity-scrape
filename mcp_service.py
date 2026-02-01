"""
Perplexity MCP Server

An MCP server that provides Perplexity AI search capabilities.
"""

import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from src.core.perplexity_client import PerplexityClient
from src.prompts import PROGRAMMING_RESEARCH_PROMPTS, VALID_CATEGORIES


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
        # Disabled by default - allows any host (typical for proxy deployments)
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)

    # Host check enabled - configure allowed hosts
    allowed_hosts = [
        "localhost",
        "localhost:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "0.0.0.0",
        "0.0.0.0:*",
    ]

    # Add custom hosts from environment variable
    custom_hosts = os.environ.get("MCP_ALLOWED_HOSTS", "")
    if custom_hosts:
        allowed_hosts.extend([h.strip() for h in custom_hosts.split(",") if h.strip()])

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
    )


# Configure transport security (disabled by default for proxy compatibility)
transport_security = get_transport_security()

mcp = FastMCP("Perplexity Search", transport_security=transport_security)
_client: Optional[PerplexityClient] = None


def get_client() -> PerplexityClient:
    """Get or create the Perplexity client."""
    global _client
    if _client is None:
        _client = PerplexityClient()
    return _client


@mcp.tool()
def perplexity_ask(
    query: str,
    mode: str = "copilot",
    model_preference: str = "claude45sonnetthinking",
    search_focus: str = "internet",
) -> dict:
    """
    Search the web using Perplexity AI.

    Args:
        query: The search query to send to Perplexity
        mode: Search mode - 'copilot' for comprehensive answers, 'search' for quick results
        model_preference: AI model to use (default: claude45sonnetthinking)
        search_focus: Focus area - 'internet' for web, 'academic' for scholarly sources

    Returns:
        Dictionary containing the search response with text, citations, and related queries
    """
    client = get_client()
    response = client.ask(
        query=query,
        mode=mode,
        model_preference=model_preference,
        search_focus=search_focus,
    )

    return {
        "text": response.text,
        "citations": response.citations,
        "related_queries": response.related_queries,
        "media_count": len(response.media_items),
    }


@mcp.tool()
def perplexity_quick_search(
    query: str, model_preference: str = "claude45sonnetthinking"
) -> str:
    """
    Quick web search using Perplexity AI. Returns just the answer text.

    Args:
        query: The search query
        model_preference: AI model to use (default: claude45sonnetthinking)

    Returns:
        The response text from Perplexity
    """
    client = get_client()
    response = client.ask(
        query=query, mode="copilot", model_preference=model_preference
    )
    return response.text


@mcp.tool()
def perplexity_academic_search(
    query: str, model_preference: str = "claude45sonnetthinking"
) -> dict:
    """
    Search academic sources using Perplexity AI.

    Args:
        topic: The topic to research
        category: Context category (e.g., "machine learning", "mathematics", "physics")
        model_preference: AI model to use (default: claude45sonnetthinking)

    Returns:
        Dictionary with research findings and citations
    """
    client = get_client()
    response = client.ask(
        query=query,
        mode="copilot",
        model_preference=model_preference,
        search_focus="academic",
        sources=["scholar"],
    )

    return {
        "text": response.text,
        "citations": response.citations,
        "related_queries": response.related_queries,
    }


@mcp.tool()
def perplexity_comprehensive_search(
    query: str, model_preference: str = "claude45sonnetthinking"
) -> dict:
    """
    Search both web and academic sources using Perplexity AI.

    Args:
        query: The search query
        model_preference: AI model to use (default: claude45sonnetthinking)

    Returns:
        Dictionary with comprehensive answer combining web and scholarly sources
    """
    client = get_client()
    response = client.ask(
        query=query,
        mode="copilot",
        model_preference=model_preference,
        search_focus="internet",
        sources=["web", "scholar"],
    )

    return {
        "text": response.text,
        "citations": response.citations,
        "related_queries": response.related_queries,
    }


@mcp.tool()
def perplexity_research(
    topic: str,
    category: str = "general",
    model_preference: str = "claude45sonnetthinking",
) -> dict:
    """
    Research a programming topic using Perplexity AI with category-specific prompts.

    Best for: Getting programming-focused research with code examples, API docs,
    implementation patterns, and best practices.

    Args:
        topic: The programming topic to research
        category: Research category - determines the prompt template used:
            - "api": API/SDK documentation and usage patterns
            - "library": Library/framework guides and integration
            - "implementation": Step-by-step implementation guidance
            - "debugging": Troubleshooting and debugging approaches
            - "comparison": Technical comparisons between options
            - "general": General programming-focused research (default)
        model_preference: AI model to use (default: claude45sonnetthinking)

    Returns:
        Dictionary with research findings, code examples, and citations
    """
    # Normalize category and validate
    normalized_category = category.lower().strip()
    if normalized_category not in VALID_CATEGORIES:
        normalized_category = "general"

    # Get the appropriate prompt template and format with topic
    prompt_template = PROGRAMMING_RESEARCH_PROMPTS[normalized_category]
    research_prompt = prompt_template.format(topic=topic)

    client = get_client()
    response = client.ask(
        query=research_prompt,
        mode="copilot",
        model_preference=model_preference,
        search_focus="internet",
        sources=["web", "scholar"],
    )

    return {
        "text": response.text,
        "citations": response.citations,
        "related_queries": response.related_queries,
    }


@mcp.tool()
def perplexity_general_research(
    topic: str,
    category: str = "general",
    model_preference: str = "claude45sonnetthinking",
) -> dict:
    """
    Research a topic using Perplexity AI with a generic/academic-focused prompt.

    Best for: Getting comprehensive background research with formal definitions,
    theorems, and academic sources. Use this for non-programming topics or when
    you want academic-style research output.

    Args:
        topic: The topic to research
        category: Context category (e.g., "machine learning", "mathematics", "physics")
        model_preference: AI model to use (default: claude45sonnetthinking)

    Returns:
        Dictionary with research findings and citations
    """
    research_prompt = f"""Research "{topic}" in the context of {category}.

Provide a comprehensive overview including:
1. **Definition and core concepts**
2. **Key principles and how it works**
3. **Practical examples and use cases**
4. **Important considerations and best practices**
5. **Related topics and further reading**

Use credible sources and cite where possible."""

    client = get_client()
    response = client.ask(
        query=research_prompt,
        mode="copilot",
        model_preference=model_preference,
        search_focus="internet",
        sources=["web", "scholar"],
    )

    return {
        "text": response.text,
        "citations": response.citations,
        "related_queries": response.related_queries,
    }


if __name__ == "__main__":
    from src.config import config

    if config.mcp_transport_mode == "http":
        # Run as HTTP server with streamable-http transport
        import uvicorn
        from src.core.mcp_auth import MCPAuthMiddleware

        # Get the Starlette app from FastMCP
        app = mcp.streamable_http_app()

        # Add authentication middleware
        app.add_middleware(MCPAuthMiddleware)

        # Run with uvicorn
        uvicorn.run(
            app,
            host=config.mcp_http_host,
            port=config.mcp_http_port,
        )
    else:
        # Default: Run as stdio server (for MCP clients like Claude Desktop)
        mcp.run()
