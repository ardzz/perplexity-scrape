"""Debugging research prompt template."""

TEMPLATE = """Research debugging approaches for "{topic}" issues in software development.

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

Include code snippets showing both problematic patterns and their fixes."""
