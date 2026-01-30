"""
Perplexity MCP Server

An MCP server that provides Perplexity AI search capabilities.
"""

import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from perplexity_client import PerplexityClient


# Programming-focused research prompt templates
# Each template is optimized for specific programming research contexts
PROGRAMMING_RESEARCH_PROMPTS = {
    "api": """Research "{topic}" API/SDK documentation and usage.

Provide a comprehensive guide including:
1. **Quick Start**: Minimal working code example with all necessary imports
2. **Authentication & Setup**: How to configure, initialize, and authenticate
3. **Key Endpoints/Methods**: Most common operations with complete code examples
4. **Request/Response Examples**: Show actual payloads and data structures
5. **Error Handling**: Common errors, status codes, and how to handle them gracefully
6. **Rate Limits & Best Practices**: Usage constraints and optimization tips
7. **Version Info**: Current stable version, breaking changes, and compatibility notes

Include complete, runnable code examples with proper imports and error handling.""",
    "library": """Research "{topic}" library/framework for software development.

Provide a comprehensive guide including:
1. **Installation & Setup**: Package manager commands, dependencies, and configuration
2. **Core Concepts**: Key abstractions, data structures, and design patterns used
3. **Quick Start Example**: Minimal working code demonstrating basic usage
4. **Common Use Cases**: Typical scenarios with complete code examples
5. **Configuration Options**: Important settings, defaults, and customization
6. **Integration Patterns**: How to integrate with other common tools/frameworks
7. **Performance Tips**: Optimization techniques and common pitfalls to avoid
8. **Version Compatibility**: Supported versions, migration guides, and deprecations

Include TypeScript/type definitions where applicable. All code examples should be complete and runnable.""",
    "implementation": """Research how to implement "{topic}" in software development.

Provide step-by-step implementation guidance:
1. **Architecture Overview**: High-level design and component interactions
2. **Prerequisites**: Required knowledge, dependencies, and setup
3. **Step-by-Step Implementation**:
   - Data models and type definitions
   - Core logic implementation with code
   - Error handling and edge cases
   - Testing approach
4. **Complete Code Example**: Full working implementation with comments
5. **Common Pitfalls**: Mistakes to avoid and debugging tips
6. **Security Considerations**: Relevant security best practices
7. **Production Readiness**: Logging, monitoring, and deployment considerations

Provide complete, production-quality code examples with proper error handling and types.""",
    "debugging": """Research debugging approaches for "{topic}" issues in software development.

Provide systematic debugging guidance:
1. **Common Causes**: Most frequent reasons for this issue
2. **Diagnostic Steps**: How to identify the root cause
   - Logging and tracing approaches
   - Debugging tools and techniques
   - Key indicators to look for
3. **Solution Patterns**: Fixes for each common cause with code examples
4. **Prevention Strategies**: How to avoid this issue in the future
5. **Related Issues**: Similar problems that may have the same symptoms
6. **Tool Recommendations**: Debuggers, profilers, and monitoring tools

Include code snippets showing both problematic patterns and their fixes.""",
    "comparison": """Research and compare options for "{topic}" in software development.

Provide an objective technical comparison:
1. **Options Overview**: Brief description of each alternative
2. **Feature Comparison Table**: Key capabilities side-by-side
3. **Performance Benchmarks**: Speed, memory, scalability metrics (with sources)
4. **Code Comparison**: Same task implemented in each option
5. **Pros and Cons**: Strengths and weaknesses of each
6. **Use Case Recommendations**: When to choose each option
7. **Community & Ecosystem**: Popularity, maintenance status, documentation quality
8. **Migration Considerations**: Switching costs between options

Include specific version numbers and benchmark data with citations.""",
    "general": """Research "{topic}" for software development purposes.

Provide a comprehensive programming-focused overview:
1. **Concept Overview**: What it is and why it matters for developers
2. **How It Works**: Technical explanation with diagrams/pseudocode if helpful
3. **Code Examples**: Practical implementations in relevant languages
4. **Common Patterns**: Typical usage patterns and idioms
5. **Best Practices**: Industry-standard approaches and recommendations
6. **Gotchas & Pitfalls**: Common mistakes and how to avoid them
7. **Tools & Libraries**: Relevant ecosystem tools
8. **Further Learning**: Documentation, tutorials, and resources

Include working code examples with proper imports and error handling.""",
}

# Valid categories for programming research
VALID_CATEGORIES = set(PROGRAMMING_RESEARCH_PROMPTS.keys())


mcp = FastMCP("Perplexity Search")
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
