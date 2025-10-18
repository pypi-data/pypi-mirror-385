# Contributing

Thank you for your interest in contributing to LLM-Dispatcher! This guide will help you get started with contributing to the project.

## Overview

We welcome contributions in many forms:

- **Bug fixes** - Fix issues and improve stability
- **New features** - Add new functionality and capabilities
- **Documentation** - Improve documentation and examples
- **Tests** - Add test coverage and improve quality
- **Performance** - Optimize performance and reduce costs
- **Security** - Enhance security and compliance features

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python and async programming
- Familiarity with LLM APIs (OpenAI, Anthropic, Google, etc.)

### Development Setup

1. **Fork the repository**

   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/your-username/llm-dispatcher.git
   cd llm-dispatcher
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**

   ```bash
   pip install -e ".[dev,docs,test]"
   ```

4. **Install pre-commit hooks**

   ```bash
   pre-commit install
   ```

5. **Run tests to ensure everything works**
   ```bash
   pytest
   ```

## Development Workflow

### Branch Strategy

We use a feature branch workflow:

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linting**

   ```bash
   pytest
   black .
   isort .
   flake8
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

**Examples:**

```
feat: add support for Google Gemini models
fix: resolve rate limiting issue with Anthropic provider
docs: update installation guide
test: add integration tests for streaming
```

## Coding Standards

### Python Style

We use the following tools for code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting

**Configuration files:**

- `pyproject.toml` - Black and isort configuration
- `.flake8` - Flake8 configuration

### Code Structure

```python
# Example of well-structured code
from typing import Dict, List, Optional
import asyncio
import logging

from llm_dispatcher.core.base import TaskRequest, TaskResponse
from llm_dispatcher.exceptions import LLMDispatcherError

logger = logging.getLogger(__name__)

class ExampleProvider:
    """Example provider implementation."""

    def __init__(self, config: Dict[str, any]):
        """Initialize the provider."""
        self.config = config
        self.name = config.get("name", "example")

    async def generate_text(self, request: TaskRequest) -> TaskResponse:
        """Generate text using the provider."""
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            raise LLMDispatcherError(f"Provider error: {e}")

    def is_healthy(self) -> bool:
        """Check if the provider is healthy."""
        return True
```

### Documentation Standards

- **Docstrings** - Use Google-style docstrings
- **Type hints** - Include type hints for all functions
- **Comments** - Explain complex logic
- **Examples** - Include usage examples

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Example function with proper documentation.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value

    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer

    Example:
        >>> result = example_function("test", 20)
        >>> print(result)
        True
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    if not isinstance(param2, int):
        raise TypeError("param2 must be an integer")

    return True
```

## Testing

### Test Structure

We use pytest for testing. Tests are organized as follows:

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── performance/    # Performance tests
└── fixtures/       # Test fixtures
```

### Writing Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

from llm_dispatcher.core.base import TaskRequest, TaskType
from llm_dispatcher.providers.openai_provider import OpenAIProvider

class TestOpenAIProvider:
    """Test cases for OpenAI provider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance for testing."""
        return OpenAIProvider({
            "name": "openai",
            "api_key": "test-key",
            "models": ["gpt-4"]
        })

    @pytest.fixture
    def request(self):
        """Create test request."""
        return TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )

    @pytest.mark.asyncio
    async def test_generate_text_success(self, provider, request):
        """Test successful text generation."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 100

            mock_client.chat.completions.create.return_value = mock_response

            result = await provider.generate_text(request)

            assert result.content == "Test response"
            assert result.tokens_used == 100
            assert result.provider == "openai"

    @pytest.mark.asyncio
    async def test_generate_text_failure(self, provider, request):
        """Test text generation failure."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_client.chat.completions.create.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                await provider.generate_text(request)

    def test_is_healthy(self, provider):
        """Test health check."""
        assert provider.is_healthy() is True
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_openai_provider.py

# Run tests with coverage
pytest --cov=llm_dispatcher --cov-report=html

# Run integration tests
pytest tests/integration/

# Run performance tests
pytest tests/performance/
```

## Adding New Features

### New Provider

1. **Create provider class**

   ```python
   # src/llm_dispatcher/providers/new_provider.py
   from llm_dispatcher.providers.base_provider import LLMProvider

   class NewProvider(LLMProvider):
       """New provider implementation."""

       def __init__(self, config: Dict[str, Any]):
           super().__init__(config)
           # Initialize provider

       async def generate_text(self, request: TaskRequest) -> TaskResponse:
           # Implement text generation
           pass
   ```

2. **Add tests**

   ```python
   # tests/unit/test_new_provider.py
   class TestNewProvider:
       # Add test cases
       pass
   ```

3. **Update documentation**

   ```markdown
   # docs/providers/new-provider.md

   # Add provider documentation
   ```

4. **Update configuration**
   ```python
   # src/llm_dispatcher/config/settings.py
   # Add provider configuration
   ```

### New Feature

1. **Plan the feature**

   - Create an issue describing the feature
   - Discuss implementation approach
   - Get feedback from maintainers

2. **Implement the feature**

   - Write code following our standards
   - Add comprehensive tests
   - Update documentation

3. **Submit pull request**
   - Include description of changes
   - Reference related issues
   - Ensure all tests pass

## Documentation

### Documentation Structure

```
docs/
├── getting-started/    # Getting started guides
├── user-guide/        # User documentation
├── api/               # API reference
├── providers/         # Provider documentation
├── benchmarks/        # Benchmarking guides
└── development/       # Development guides
```

### Writing Documentation

- **Use clear, concise language**
- **Include code examples**
- **Keep documentation up to date**
- **Use proper markdown formatting**

````markdown
# Feature Name

Brief description of the feature.

## Overview

Detailed explanation of what the feature does and why it's useful.

## Usage

### Basic Usage

```python
from llm_dispatcher import feature_name

# Example code
result = feature_name.example_function()
print(result)
```
````

### Advanced Usage

```python
# More complex example
# with detailed explanation
```

## Configuration

| Option    | Type  | Default     | Description            |
| --------- | ----- | ----------- | ---------------------- |
| `option1` | `str` | `"default"` | Description of option1 |
| `option2` | `int` | `100`       | Description of option2 |

## Examples

### Example 1: Basic Usage

```python
# Example code
```

### Example 2: Advanced Usage

```python
# More complex example
```

## Best Practices

1. **Best practice 1**
2. **Best practice 2**
3. **Best practice 3**

## Next Steps

- [Link to related documentation](../getting-started/examples.md)
- [Link to examples](../getting-started/examples.md)

````

## Code Review Process

### Pull Request Requirements

1. **All tests must pass**
2. **Code coverage must not decrease**
3. **Documentation must be updated**
4. **Code must follow style guidelines**
5. **Pull request must be up to date**

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] Performance impact is considered
- [ ] Security implications are reviewed
- [ ] Breaking changes are documented

### Review Process

1. **Automated checks** - CI/CD pipeline runs tests and linting
2. **Maintainer review** - At least one maintainer reviews the code
3. **Community feedback** - Community members can provide feedback
4. **Final approval** - Maintainer approves and merges the PR

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update changelog** in `CHANGELOG.md`
3. **Create release tag**
4. **Build and publish** to PyPI
5. **Update documentation**

## Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct:

- **Be respectful** - Treat everyone with respect
- **Be inclusive** - Welcome contributors from all backgrounds
- **Be constructive** - Provide helpful feedback
- **Be patient** - Remember that everyone is learning

### Getting Help

- **GitHub Issues** - For bug reports and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Discord** - For real-time chat and support
- **Email** - For security issues and private matters

### Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** - List of all contributors
- **Release notes** - Contributors for each release
- **Documentation** - Contributors for specific features

## Best Practices

### 1. **Start Small**
```python
# Good: Start with a simple implementation
def simple_function(param: str) -> str:
    """Simple function that does one thing well."""
    return param.upper()

# Avoid: Complex implementation from the start
def complex_function(param: str, config: dict, options: list) -> dict:
    """Complex function that does too many things."""
    # Too much complexity
    pass
````

### 2. **Write Tests First**

```python
# Good: Write tests before implementation
def test_new_feature():
    """Test new feature before implementing."""
    result = new_feature("input")
    assert result == "expected_output"

# Avoid: Writing tests after implementation
# Implementation first, tests later
```

### 3. **Document as You Go**

```python
# Good: Document while writing code
def documented_function(param: str) -> str:
    """Function with clear documentation.

    Args:
        param: Input parameter

    Returns:
        Processed result
    """
    return param.upper()

# Avoid: Adding documentation later
def undocumented_function(param: str) -> str:
    return param.upper()
```

### 4. **Follow Existing Patterns**

```python
# Good: Follow existing code patterns
class NewProvider(LLMProvider):
    """New provider following existing pattern."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Follow existing initialization pattern

    async def generate_text(self, request: TaskRequest) -> TaskResponse:
        # Follow existing implementation pattern
        pass

# Avoid: Creating new patterns without discussion
class CompletelyDifferentProvider:
    # Different pattern that doesn't fit
    pass
```

### 5. **Ask for Help**

```python
# Good: Ask for help when needed
# Create GitHub issue or discussion
# Ask in Discord
# Reach out to maintainers

# Avoid: Struggling alone
# Don't hesitate to ask questions
```

## Next Steps

- [:octicons-book-24: Code of Conduct](code-of-conduct.md) - Community guidelines
- [:octicons-beaker-24: Testing](testing.md) - Testing guidelines and best practices
- [:octicons-history-24: Changelog](changelog.md) - Project changelog and release notes
- [:octicons-shield-check-24: Security](security.md) - Security guidelines and reporting
