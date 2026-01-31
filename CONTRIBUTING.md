# Contributing to Perplexity MCP

First off, thank you for considering contributing to Perplexity MCP! We welcome contributions of all kinds and appreciate your interest in making this project better.

Please read and follow our [Code of Conduct](#code-of-conduct) to help us maintain a welcoming and inclusive community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Security Vulnerabilities](#security-vulnerabilities)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please read the full text so that you can understand what actions will and will not be tolerated.

## How Can I Contribute?

### Bug Fixes

Found a bug? We'd love to hear about it! Submit a detailed bug report with:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Your environment (Python version, OS, etc.)

### Features

Have an idea for a new feature? Consider opening an issue first to discuss it with the maintainers. This helps ensure the feature aligns with the project's direction.

### Documentation

Help improve our documentation by:
- Fixing typos or unclear explanations
- Adding examples
- Improving code comments
- Enhancing the README or API docs

### Testing

Improve test coverage by:
- Writing tests for new features
- Adding edge case tests
- Improving existing test reliability

## Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/perplexity-mcp.git
   cd perplexity-mcp
   ```

2. **Set Up Your Fork**
   ```bash
   git remote add upstream https://github.com/ardzz/perplexity-mcp.git
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Reference the README**
   For project setup and running instructions, see the [README.md](README.md).

## Development Setup

### Requirements

- **Python 3.12+** (required)
- pip (or another package manager)

### Installation

1. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Perplexity credentials
   ```

   See `.env.example` for configuration details.

### Verify Installation

```bash
python -c "import mcp; print('Setup successful!')"
```

## Project Structure

```
perplexity-mcp/
├── mcp_service.py          # MCP server entry point
├── rest_api_service.py     # REST API server entry point
├── unified_service.py      # Combined server (REST + MCP)
├── src/                    # Main source code
│   ├── api/               # REST API implementation
│   ├── mcp/               # MCP server implementation
│   └── core/              # Core utilities and business logic
├── tests/                 # Test suite (pytest)
├── requirements.txt       # Python dependencies
├── .env.example          # Example configuration
└── README.md             # Project documentation
```

## Code Style

### PEP 8 Compliance

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style:
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Type Hints

We require type hints for all functions and classes:

```python
def fetch_search_results(
    query: str, 
    model: str = "claude-4.5-sonnet"
) -> list[dict[str, Any]]:
    """Fetch search results from Perplexity API."""
    pass
```

### Docstrings

All public functions and classes must have docstrings using the Google style:

```python
def search(query: str, focus: str = "internet") -> dict:
    """Perform a web search query.
    
    Args:
        query: The search query string.
        focus: Search focus - 'internet' or 'academic'. Defaults to 'internet'.
        
    Returns:
        A dictionary containing search results and citations.
        
    Raises:
        ValueError: If query is empty.
        ConnectionError: If unable to reach Perplexity API.
    """
    pass
```

### Import Organization

```python
# Standard library
import os
from typing import Any

# Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# Local
from src.core.search import PerplexitySearch
```

## Testing

We use **pytest** for testing. All new code must include tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_mcp_service.py

# Run specific test
pytest tests/test_mcp_service.py::test_search_functionality
```

### Writing Tests

```python
import pytest
from src.api.client import PerplexityClient

@pytest.fixture
def client():
    """Provide a test client."""
    return PerplexityClient()

def test_search_returns_results(client):
    """Test that search returns valid results."""
    results = client.search("Python programming")
    assert len(results) > 0
    assert "content" in results[0]
```

### Test Coverage

- Aim for >80% code coverage
- Test both success and error cases
- Include edge cases and boundary conditions

## Pull Request Process

### Before Submitting

1. **Update from Main Branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run Tests**
   ```bash
   pytest
   ```

3. **Check Code Style**
   ```bash
   python -m flake8 src/
   python -m mypy src/
   ```

### Branch Naming

Use descriptive branch names:
- `feature/short-description` for new features
- `fix/short-description` for bug fixes
- `docs/short-description` for documentation
- `test/short-description` for tests

### Commit Messages

Write clear, concise commit messages:

```
Short summary (50 characters or less)

More detailed explanation of the change if needed.
Explain what and why, not how.

Fixes #123
```

### Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] Type hints are included
- [ ] Docstrings are present and clear
- [ ] Tests are written and passing (`pytest`)
- [ ] Code coverage hasn't decreased
- [ ] No debugging statements (print, pdb) left in
- [ ] Commit messages are clear and descriptive
- [ ] Documentation is updated if needed
- [ ] Python 3.12+ compatibility verified

### PR Description Template

```markdown
## Description
Brief explanation of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Test improvement

## Related Issue
Fixes #123

## Testing
Describe how you tested the changes

## Checklist
- [ ] Tests passing
- [ ] Code style followed
- [ ] Documentation updated
```

## Reporting Issues

### Bug Reports

Create a GitHub issue with:

1. **Clear Title**: Summarize the problem
2. **Description**: Explain what happened
3. **Steps to Reproduce**
   ```
   1. Configure environment with...
   2. Run...
   3. See error...
   ```
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happened
6. **Environment**:
   - Python version: `python --version`
   - OS: Windows/macOS/Linux
   - Relevant dependencies versions

### Feature Requests

Suggest features by opening an issue with:

1. **Clear Title**: Summarize the feature
2. **Description**: Explain the use case
3. **Benefits**: Why is this useful?
4. **Alternatives**: Any workarounds?

## Security Vulnerabilities

**IMPORTANT**: Do not report security vulnerabilities as public GitHub issues.

Instead, please email security concerns directly to the maintainers. We will:
1. Acknowledge receipt within 48 hours
2. Provide an assessment and timeline
3. Work with you on a fix
4. Credit you in the security advisory (if you wish)

Include in your report:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

---

## Questions?

Feel free to open an issue or discussion if you have questions about contributing. We're here to help!

Thank you for contributing to Perplexity MCP! 🚀
