"""
Perplexity MCP Server

An MCP server that provides Perplexity AI search capabilities.
"""

import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from src.core.perplexity_client import PerplexityClient


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
    # ==================== ML/DL Research Templates ====================
    # These templates follow a hybrid format: mathematical rigor + practical code
    # Designed for machine learning and deep learning research queries
    "ml_architecture": """Research "{topic}" neural network architecture in machine learning/deep learning.

Provide a rigorous yet accessible explanation with mathematical foundations:

1. **Formal Definition**: 
   - Precise mathematical definition of the architecture
   - Use LaTeX notation for all equations (e.g., $f(x) = Wx + b$)
   - Define all variables and their dimensions explicitly

2. **Intuition & Motivation**:
   - Why was this architecture developed? What problem does it solve?
   - Visual mental model: describe how data flows through the architecture
   - Historical context and evolution from prior architectures

3. **Mathematical Formulation**:
   - Forward pass equations with full derivation
   - Key operations (convolution, attention, etc.) with tensor dimensions
   - Complexity analysis: time and space complexity in Big-O notation

4. **Architecture Components**:
   - Layer-by-layer breakdown with input/output shapes
   - Activation functions and their mathematical properties
   - Normalization, regularization, and other components

5. **Code Implementation**:
   - Complete, runnable implementation in PyTorch (preferred) or TensorFlow
   - Include all imports, layer definitions, and forward method
   - Show example usage with dummy data and correct tensor shapes

6. **Training Considerations**:
   - Appropriate loss functions and why
   - Initialization strategies (Xavier, He, etc.) with mathematical justification
   - Common hyperparameters and their typical ranges

7. **Practical Exercises**:
   - Exercise 1: Implement a simplified version from scratch (numpy only)
   - Exercise 2: Modify the architecture for a specific use case
   - Include expected outputs to verify correctness

8. **Key Papers & References**:
   - Original paper with arXiv link if available
   - Follow-up improvements and variants
   - Benchmark results on standard datasets

Use proper mathematical notation throughout. All equations should be in LaTeX format.""",
    "ml_training": """Research "{topic}" training procedure/optimization in machine learning/deep learning.

Provide a mathematically rigorous explanation of the training algorithm:

1. **Formal Definition**:
   - Mathematical formulation of the optimization objective
   - Loss function definition with LaTeX: $\\mathcal{{L}}(\\theta) = ...$
   - Gradient computation: $\\nabla_\\theta \\mathcal{{L}} = ...$

2. **Algorithm Derivation**:
   - Step-by-step derivation from first principles
   - Show how the update rule is obtained
   - For momentum-based methods: derive the exponential moving average

3. **Update Rules**:
   - Parameter update equation: $\\theta_{{t+1}} = \\theta_t - \\alpha \\cdot g_t$
   - Any auxiliary variables (momentum, adaptive learning rates)
   - Bias correction terms if applicable

4. **Convergence Analysis**:
   - Convergence guarantees (convex vs non-convex)
   - Learning rate requirements for convergence
   - Regret bounds if applicable

5. **Pseudocode & Implementation**:
   - Clear pseudocode showing the complete algorithm
   - PyTorch implementation: both using built-in optimizer and from scratch
   - Comparison showing they produce identical results

6. **Hyperparameter Guidance**:
   - Learning rate: typical ranges and scheduling strategies
   - Momentum/beta parameters: default values and when to adjust
   - Batch size effects on training dynamics

7. **Practical Considerations**:
   - Gradient clipping: when and how
   - Learning rate warmup and decay schedules
   - Debugging tips: what gradient magnitudes to expect

8. **Exercises**:
   - Derive the gradient for a simple loss function by hand
   - Implement the optimizer from scratch and verify against PyTorch
   - Visualize the optimization trajectory on a simple 2D function

9. **References**:
   - Original paper introducing the method
   - Key improvements and variants
   - Empirical comparisons on benchmark tasks

All mathematical derivations should be complete and verifiable.""",
    "ml_concepts": """Research "{topic}" concept in machine learning/deep learning.

Provide a comprehensive explanation with theoretical foundations:

1. **Formal Definition**:
   - Rigorous mathematical definition using proper notation
   - LaTeX equations for all formulas
   - Clearly define all terms and symbols used

2. **Intuitive Explanation**:
   - Plain-language explanation accessible to beginners
   - Analogies and visual mental models
   - Why this concept matters in practice

3. **Mathematical Framework**:
   - Theoretical foundations and assumptions
   - Key theorems and their implications
   - Proof sketches for important results

4. **Relationship to Other Concepts**:
   - How this connects to related ML concepts
   - Prerequisites for understanding
   - What this concept enables (downstream applications)

5. **Detection & Measurement**:
   - How to identify/measure this concept in practice
   - Metrics and diagnostic tools
   - Visual indicators (learning curves, etc.)

6. **Practical Solutions**:
   - Techniques to address or leverage this concept
   - Code examples showing each technique
   - Trade-offs between different approaches

7. **Code Demonstration**:
   - Complete Python example demonstrating the concept
   - Visualization code (matplotlib/seaborn)
   - Before/after comparison where applicable

8. **Common Misconceptions**:
   - Frequently misunderstood aspects
   - Clarifications with concrete examples
   - Edge cases and exceptions

9. **Exercises**:
   - Theoretical: prove a related result or derive a formula
   - Practical: implement detection/mitigation in code
   - Analysis: interpret given experimental results

10. **Further Reading**:
    - Seminal papers and textbook chapters
    - Online resources and tutorials
    - Research directions and open questions

Emphasize both mathematical rigor and practical applicability.""",
    "ml_frameworks": """Research "{topic}" in the context of ML/DL frameworks (PyTorch, TensorFlow, JAX, etc.).

Provide framework-specific guidance with implementation details:

1. **Concept Overview**:
   - What this feature/API does and why it's important
   - Which frameworks support it and naming differences
   - When to use this vs alternatives

2. **API Reference**:
   - Function/class signature with all parameters
   - Parameter types and default values
   - Return types and shapes

3. **Under the Hood**:
   - How the framework implements this internally
   - Computational graph implications
   - Memory and performance characteristics

4. **Basic Usage**:
   - Minimal working example with imports
   - Step-by-step explanation of the code
   - Expected output with tensor shapes

5. **Advanced Patterns**:
   - Custom implementations and extensions
   - Integration with training loops
   - Multi-GPU/distributed considerations

6. **Framework Comparison**:
   - PyTorch implementation
   - TensorFlow/Keras equivalent
   - JAX/Flax approach if applicable
   - Highlight API differences and gotchas

7. **Performance Optimization**:
   - Efficient usage patterns
   - Common performance pitfalls
   - Profiling and benchmarking approach

8. **Debugging Guide**:
   - Common errors and their solutions
   - Shape mismatch debugging
   - Gradient flow verification

9. **Complete Example**:
   - Full working code integrating with a training pipeline
   - Include data loading, model definition, training loop
   - Show checkpointing and inference

10. **Best Practices**:
    - Official recommendations from framework documentation
    - Community conventions and patterns
    - Version compatibility notes

All code should be complete, runnable, and follow framework conventions.""",
    "ml_math": """Research "{topic}" mathematical foundations for machine learning.

Provide a rigorous mathematical treatment suitable for ML practitioners:

1. **Formal Definition**:
   - Precise mathematical definition with all notation explained
   - Domain and range specifications
   - Prerequisites from prerequisite fields (linear algebra, calculus, probability)

2. **Intuitive Understanding**:
   - Geometric or visual interpretation
   - Connections to familiar concepts
   - Why ML practitioners need this

3. **Key Theorems & Properties**:
   - State important theorems precisely using LaTeX
   - Proof or proof sketch for each
   - Conditions under which theorems hold

4. **Derivations**:
   - Step-by-step derivation of key results
   - Show all algebraic steps explicitly
   - Highlight common techniques used (chain rule, etc.)

5. **Computational Methods**:
   - Algorithms for computing/evaluating
   - Numerical stability considerations
   - Efficient implementations

6. **Applications in ML**:
   - Specific ML algorithms that use this concept
   - How the math translates to code
   - Real-world examples with data

7. **NumPy/PyTorch Implementation**:
   - Pure NumPy implementation from first principles
   - Comparison with built-in functions
   - Verification of correctness

8. **Worked Examples**:
   - Detailed numerical examples solved by hand
   - Corresponding code verification
   - Visualization where helpful

9. **Exercises**:
   - Proof exercise: derive a related result
   - Computation exercise: calculate by hand, verify with code
   - Application exercise: use in an ML context

10. **References**:
    - Textbook chapters (Bishop, Murphy, Goodfellow)
    - Online lecture notes (Stanford CS229, MIT 18.06)
    - Foundational papers if applicable

All equations must be in proper LaTeX notation. Show complete derivations.""",
    "ml_paper": """Research "{topic}" machine learning paper/research contribution.

Provide a comprehensive paper analysis and implementation guide:

1. **Paper Overview**:
   - Full citation with authors, venue, year
   - arXiv link and official code repository if available
   - One-paragraph summary of the contribution

2. **Problem Statement**:
   - What problem does the paper address?
   - Why was this problem important at the time?
   - Prior approaches and their limitations

3. **Key Contributions**:
   - List the main contributions (typically 3-5)
   - Novel techniques or insights introduced
   - Theoretical vs empirical contributions

4. **Method/Architecture**:
   - Detailed explanation of the proposed approach
   - Mathematical formulation with all equations
   - Architecture diagram description (if applicable)

5. **Key Equations**:
   - The most important equations from the paper
   - Explanation of each term and variable
   - How these differ from prior work

6. **Implementation Details**:
   - Hyperparameters used in experiments
   - Training procedure specifics
   - Data preprocessing and augmentation

7. **Reproduction Code**:
   - Minimal PyTorch implementation of the key idea
   - Focus on the novel contribution, not full paper
   - Include verification against paper's reported results if possible

8. **Experimental Results**:
   - Summary of main results and benchmarks
   - Comparison with baselines
   - Ablation studies and their insights

9. **Critical Analysis**:
   - Strengths of the approach
   - Limitations and failure cases
   - Assumptions that may not hold in practice

10. **Impact & Follow-ups**:
    - How influential has this paper been?
    - Important follow-up works and improvements
    - Current state-of-the-art in comparison

11. **Study Questions**:
    - Questions to test understanding of the paper
    - Implementation challenges to attempt
    - Extensions to explore

Provide enough detail that someone could implement the key ideas from your summary.""",
    "ml_debugging": """Research "{topic}" debugging issue in machine learning/deep learning.

Provide systematic debugging guidance with mathematical insights:

1. **Problem Description**:
   - Clear definition of the issue
   - How it manifests in training (loss curves, metrics, outputs)
   - Mathematical explanation of why this happens

2. **Root Causes**:
   - List all common causes with mathematical reasoning
   - For each cause: why it leads to this symptom
   - Probability/frequency of each cause

3. **Diagnostic Process**:
   - Step-by-step debugging procedure
   - What to check first (most likely causes)
   - Specific values/behaviors to look for

4. **Detection Code**:
   - Python functions to detect the issue
   - Gradient checking utilities
   - Visualization code for diagnosis

5. **Mathematical Analysis**:
   - Formal analysis of when/why the issue occurs
   - Relevant theorems or bounds
   - Conditions that trigger the problem

6. **Solutions & Fixes**:
   - For each root cause: specific solution
   - Code changes required
   - Hyperparameter adjustments

7. **Prevention Strategies**:
   - Best practices to avoid this issue
   - Architectural choices that help
   - Initialization and normalization techniques

8. **Verification**:
   - How to verify the fix worked
   - Expected behavior after resolution
   - Regression testing approach

9. **Complete Example**:
   - Code demonstrating the problem
   - Code showing the diagnosis
   - Code implementing the fix
   - Before/after comparison

10. **Related Issues**:
    - Other problems with similar symptoms
    - How to differentiate between them
    - Issues that often co-occur

11. **Debugging Checklist**:
    - Quick reference checklist for this issue
    - Commands/snippets to run
    - Expected outputs at each step

Include complete, runnable code for all diagnostic and fix examples.""",
}

# Valid categories for programming research
VALID_CATEGORIES = set(PROGRAMMING_RESEARCH_PROMPTS.keys())


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
