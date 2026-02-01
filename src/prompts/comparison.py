"""Comparison research prompt template."""

TEMPLATE = """Research and compare options for "{topic}" in software development.

Provide an objective technical comparison:
1. **Options Overview**: Brief description of each alternative
2. **Feature Comparison Table**: Key capabilities side-by-side
3. **Performance Benchmarks**: Speed, memory, scalability metrics (with sources)
4. **Code Comparison**: Same task implemented in each option
5. **Pros and Cons**: Strengths and weaknesses of each
6. **Use Case Recommendations**: When to choose each option
7. **Community & Ecosystem**: Popularity, maintenance status, documentation quality
8. **Migration Considerations**: Switching costs between options

Include specific version numbers and benchmark data with citations."""
