"""API/SDK research prompt template."""

TEMPLATE = """Research "{topic}" API/SDK documentation and usage.

Provide a comprehensive guide including:
1. **Quick Start**: Minimal working code example with all necessary imports
2. **Authentication & Setup**: How to configure, initialize, and authenticate
3. **Key Endpoints/Methods**: Most common operations with complete code examples
4. **Request/Response Examples**: Show actual payloads and data structures
5. **Error Handling**: Common errors, status codes, and how to handle them gracefully
6. **Rate Limits & Best Practices**: Usage constraints and optimization tips
7. **Version Info**: Current stable version, breaking changes, and compatibility notes

Include complete, runnable code examples with proper imports and error handling."""
