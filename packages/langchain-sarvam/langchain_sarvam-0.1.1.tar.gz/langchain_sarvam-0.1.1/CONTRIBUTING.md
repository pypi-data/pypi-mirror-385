# Contributing to langchain-sarvam

Thank you for your interest in contributing to **langchain-sarvam**! This document provides guidelines and information for contributors.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Style and Quality](#code-style-and-quality)
- [Testing](#testing)
- [Building and Publishing](#building-and-publishing)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Reporting Issues](#reporting-issues)

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/parth1609/langchain_sarvam.git
   cd langchain_sarvam
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync --all-extras --dev
   ```

3. **Set up environment variables:**
   ```bash
   # Copy .env.example to .env and fill in your values
   cp .env.example .env

   # Or set directly
   export SARVAM_API_KEY="your_api_key_here"
   ```

### Development Commands

Use the provided Makefile for common development tasks:

```bash
# Run all linters and formatters
make lint

# Format code
make format

# Run unit tests
make test

# Run integration tests
make integration_tests

# Check imports
make check_imports

# Show available commands
make help
```

## Code Style and Quality

### Linting and Formatting

This project uses:
- **[ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[mypy](https://mypy.readthedocs.io/)**: Static type checker

**Run linting:**
```bash
uv run --all-groups ruff check .
uv run --all-groups ruff format . --diff
uv run --all-groups mypy . --cache-dir .mypy_cache
```

**Auto-format code:**
```bash
uv run --all-groups ruff format .
uv run --all-groups ruff check --fix .
```

### Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions, classes, and methods
- Keep line length under 88 characters (Black/ruff default)
- Use descriptive variable names
- Add comments for complex logic

### Import Organization

- Use absolute imports within the package
- Group imports: standard library, third-party, local
- Sort imports alphabetically within each group
- Use `from __future__ import annotations` for modern type annotations

## Testing

### Test Structure

```
tests/
├── unit_tests/          # Unit tests
└── integration_tests/   # Integration tests
```

### Running Tests

**Unit tests:**
```bash
# Run all unit tests
uv run --group test pytest --disable-socket --allow-unix-socket tests/unit_tests -q

# Run specific test file
uv run --group test pytest tests/unit_tests/test_file.py

# Run with coverage
uv run --group test pytest --cov=langchain_sarvam tests/unit_tests/
```

**Integration tests:**
```bash
# Run integration tests (requires API access)
uv run --group test --group test_integration pytest --retries 3 --retry-delay 1 tests/integration_tests/
```

**Windows-specific notes:**
- Tests use `pytest-socket` with `--disable-socket` to prevent network calls
- Async tests are marked with `@pytest.mark.enable_socket` when network access is needed
- Use `--allow-unix-socket` flag on Windows for proper asyncio support

### Writing Tests

- Write unit tests for all new functionality
- Use descriptive test names that explain what is being tested
- Mock external dependencies (API calls, file I/O, etc.)
- Test both success and failure scenarios
- Include docstrings for complex test setups
- Aim for high test coverage (>80%)

**Example test structure:**
```python
import pytest
from langchain_sarvam import ChatSarvam

class TestChatSarvam:
    def test_initialization(self):
        """Test ChatSarvam initialization with valid parameters."""
        llm = ChatSarvam(model="sarvam-m", temperature=0.5)
        assert llm.model == "sarvam-m"
        assert llm.temperature == 0.5

    def test_invalid_temperature(self):
        """Test that invalid temperature raises ValueError."""
        with pytest.raises(ValueError):
            ChatSarvam(temperature=2.0)
```

## Building and Publishing

### Building the Package

**Using uv (recommended):**
```bash
uv build
```

**Using build:**
```bash
python -m build
```

This creates distribution files in the `dist/` directory:
- `langchain_sarvam-0.1.0.tar.gz` (source distribution)
- `langchain_sarvam-0.1.0-py3-none-any.whl` (wheel)

### Publishing Process

**Automated Publishing:**
1. Create a new Git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

2. Create a GitHub release (triggers automated publishing via GitHub Actions)

**Manual Publishing:**
```bash
# Build and publish with uv
uv build
uv publish --token $PYPI_API_TOKEN

# Or using twine
pip install twine
twine upload dist/* --username=__token__ --password=$PYPI_API_TOKEN
```

## Git Workflow

### Branch Naming

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/`: New features (e.g., `feature/add-streaming-support`)
- `bugfix/`: Bug fixes (e.g., `bugfix/fix-api-timeout`)
- `hotfix/`: Critical fixes for production

### Commit Guidelines

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (Add, Fix, Update, Remove, etc.)
- Keep first line under 50 characters
- Add detailed description for complex changes

**Examples:**
```
Add streaming support for ChatSarvam

- Implement async streaming iterator
- Add streaming parameter to __init__
- Update documentation with streaming examples
- Add tests for streaming functionality
```

```
Fix API timeout handling

Timeout was not being properly passed to the underlying
SarvamAI client. This fix ensures timeouts are respected
in all API calls.
```

### Pull Request Process

1. **Fork the repository** (if you're not a maintainer)
2. **Create a feature branch** from `main` or `develop`
3. **Make your changes** following the guidelines above
4. **Run tests and linting** locally
5. **Commit your changes** with clear messages
6. **Push to your fork/branch**
7. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference any related issues
   - Screenshots/videos for UI changes

## Code Review Guidelines

### For Reviewers

- Be constructive and respectful
- Focus on code quality, not personal preferences
- Request changes, don't demand them
- Explain reasoning for requested changes
- Acknowledge good work

### For Contributors

- Address all review comments
- Ask for clarification if needed
- Don't take feedback personally
- Keep discussions focused on code

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes without discussion
- [ ] Performance implications considered
- [ ] Security implications reviewed

## Reporting Issues

### Bug Reports

**Please include:**
- Clear title describing the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Full error messages and stack traces
- Code snippets demonstrating the issue

### Feature Requests

**Please include:**
- Clear description of the proposed feature
- Use case and why it's needed
- Potential implementation approach
- Any breaking changes considerations

### Security Issues

- **DO NOT** report security vulnerabilities publicly
- Email the maintainer directly at: [parthgajananpatil@gmail.com](mailto:parthgajananpatil@gmail.com)
- Include detailed information about the vulnerability

---

## Recognition

Contributors will be acknowledged in the project's README and changelog. Significant contributions may lead to maintainer status.

Thank you for contributing to langchain-sarvam! 🎉
