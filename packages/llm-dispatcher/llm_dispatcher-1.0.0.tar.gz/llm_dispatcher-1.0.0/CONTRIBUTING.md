# Contributing to LLM-Dispatcher

Thank you for your interest in contributing to LLM-Dispatcher! We welcome contributions from the community and appreciate your help in making this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Testing](#testing)
- [Code Style](#code-style)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@llm-dispatcher.com.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- API keys for at least one LLM provider (OpenAI, Anthropic, or Google)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/llm-dispatcher.git
   cd llm-dispatcher
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ashhadahsan/llm-dispatcher.git
   ```

## Development Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install the package in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (at least one required)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Optional: Redis for advanced caching
REDIS_URL=redis://localhost:6379

# Optional: Database for analytics
DATABASE_URL=sqlite:///llm_dispatcher.db
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=llm_dispatcher --cov-report=html

# Run specific test categories
pytest tests/test_basic.py
pytest tests/test_integration.py
pytest tests/test_performance.py
```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Fixes**: Fix issues in the codebase
2. **New Features**: Add new functionality
3. **Documentation**: Improve or add documentation
4. **Tests**: Add or improve test coverage
5. **Performance**: Optimize existing code
6. **Examples**: Add usage examples
7. **Provider Integration**: Add support for new LLM providers

### Development Workflow

1. **Create a Branch**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number
   ```

2. **Make Changes**

   - Write your code following our [Code Style](#code-style) guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**

   ```bash
   # Run tests
   pytest

   # Run linting
   flake8 src/

   # Format code
   black src/ tests/
   isort src/ tests/
   ```

4. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

### Before Submitting

- [ ] Ensure all tests pass
- [ ] Update documentation if needed
- [ ] Add tests for new functionality
- [ ] Ensure code follows style guidelines
- [ ] Update CHANGELOG.md if applicable

### Pull Request Template

When creating a pull request, please include:

1. **Description**: Clear description of what the PR does
2. **Type**: Bug fix, feature, documentation, etc.
3. **Testing**: How you tested the changes
4. **Breaking Changes**: Any breaking changes
5. **Related Issues**: Link to related issues

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Maintainers review the code
3. **Testing**: Changes are tested in various environments
4. **Approval**: At least one maintainer approval required

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, package version
6. **Code Sample**: Minimal code sample that reproduces the issue
7. **Error Messages**: Full error messages and stack traces

### Issue Template

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Environment**

- OS: [e.g. macOS, Windows, Linux]
- Python Version: [e.g. 3.8, 3.9, 3.10]
- Package Version: [e.g. 0.1.0]

**Additional Context**
Add any other context about the problem here.
```

## Feature Requests

When requesting features, please include:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature would be useful
3. **Proposed Solution**: How you think it should work
4. **Alternatives**: Other solutions you've considered
5. **Additional Context**: Any other relevant information

## Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Update API documentation for code changes
- Follow the existing documentation structure

### Documentation Types

1. **API Documentation**: Docstrings for all public methods
2. **User Guides**: Step-by-step tutorials
3. **Examples**: Working code examples
4. **Reference**: Complete API reference

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## Testing

### Test Categories

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **Performance Tests**: Test scalability and performance
4. **End-to-End Tests**: Test complete workflows

### Writing Tests

```python
import pytest
from llm_dispatcher import LLMSwitch, TaskRequest, TaskType

def test_basic_functionality():
    """Test basic LLM switching functionality."""
    # Arrange
    switch = LLMSwitch(providers=[])
    request = TaskRequest(
        prompt="Test prompt",
        task_type=TaskType.TEXT_GENERATION
    )

    # Act
    decision = switch.select_llm(request)

    # Assert
    assert decision is not None
    assert decision.provider in ["openai", "anthropic", "google"]

@pytest.mark.asyncio
async def test_async_functionality():
    """Test async LLM execution."""
    # Test implementation
    pass
```

### Test Requirements

- All new code must have tests
- Maintain test coverage above 80%
- Include both positive and negative test cases
- Test error conditions and edge cases

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all public functions
- Use docstrings for all public classes and functions
- Follow the existing code style in the project

### Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **pre-commit**: Git hooks

### Running Style Checks

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/
```

### Pre-commit Hooks

Pre-commit hooks automatically run style checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**: Update version in `pyproject.toml`
2. **Update Changelog**: Add release notes to `CHANGELOG.md`
3. **Create Release Branch**: `git checkout -b release/v0.1.0`
4. **Final Testing**: Run full test suite
5. **Create Pull Request**: Merge release branch
6. **Tag Release**: Create git tag
7. **Build Package**: Build and upload to PyPI
8. **Update Documentation**: Update docs for new version

## Community

### Getting Help

- **GitHub Discussions**: Ask questions and discuss ideas
- **GitHub Issues**: Report bugs and request features
- **Email**: Contact maintainers at maintainers@llm-dispatcher.com

### Contributing to Discussions

- Be respectful and constructive
- Search existing discussions before creating new ones
- Use clear, descriptive titles
- Provide context and examples

## Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Contributors for each release
- **Documentation**: Contributors mentioned in docs

## License

By contributing to LLM-Dispatcher, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have any questions about contributing, please:

1. Check existing documentation
2. Search GitHub issues and discussions
3. Create a new discussion
4. Contact maintainers

Thank you for contributing to LLM-Dispatcher! 🚀
