"""
Perplexity MCP Server

An MCP server that provides Perplexity AI search capabilities.
"""

import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from perplexity_client import PerplexityClient


# Initialize the MCP server
mcp = FastMCP("Perplexity Search")

# Initialize client lazily to avoid startup errors
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
        "citations": response.citations[:10],  # Limit citations
        "related_queries": response.related_queries,
        "media_count": len(response.media_items),
    }


@mcp.tool()
def perplexity_quick_search(query: str) -> str:
    """
    Quick web search using Perplexity AI. Returns just the answer text.
    
    Args:
        query: The search query
        
    Returns:
        The response text from Perplexity
    """
    client = get_client()
    response = client.ask(query=query, mode="copilot")
    return response.text


@mcp.tool()
def perplexity_academic_search(query: str) -> dict:
    """
    Search academic sources using Perplexity AI.
    
    Args:
        query: The academic/research query
        
    Returns:
        Dictionary with scholarly answer and citations
    """
    client = get_client()
    response = client.ask(
        query=query,
        mode="copilot",
        search_focus="academic",
        sources=["scholar"],
    )
    
    return {
        "text": response.text,
        "citations": response.citations[:10],
        "related_queries": response.related_queries,
    }


if __name__ == "__main__":
    # Run with stdio transport for MCP
    mcp.run()
