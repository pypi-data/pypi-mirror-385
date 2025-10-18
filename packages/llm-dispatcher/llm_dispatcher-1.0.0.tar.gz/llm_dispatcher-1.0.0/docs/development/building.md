# Building and Development

Guide for building and developing LLM-Dispatcher from source.

## Prerequisites

### System Requirements

- Python 3.8 or higher
- Git
- Make (optional, for build scripts)

### Development Tools

- Virtual environment (venv, conda, or poetry)
- Code editor (VS Code, PyCharm, etc.)
- Git client

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ashhadahsan/llm-dispatcher.git
cd llm-dispatcher
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n llm-dispatcher python=3.9
conda activate llm-dispatcher

# Using poetry
poetry install
```

### 3. Install Development Dependencies

```bash
# Install in development mode
pip install -e ".[dev,docs,test]"

# Or install specific groups
pip install -e ".[dev]"      # Development tools
pip install -e ".[docs]"     # Documentation tools
pip install -e ".[test]"     # Testing tools
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

## Building from Source

### Build the Package

```bash
# Build source distribution
python -m build --sdist

# Build wheel distribution
python -m build --wheel

# Build both
python -m build
```

### Build Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=llm_dispatcher --cov-report=html

# Run specific test file
pytest tests/test_openai_provider.py

# Run tests in parallel
pytest -n auto
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Run tests
pytest
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## Build Scripts

### Makefile (if available)

```bash
# Install dependencies
make install

# Run tests
make test

# Build package
make build

# Build documentation
make docs

# Clean build artifacts
make clean
```

### Custom Build Scripts

```bash
# Run build script
./scripts/build.sh

# Run test script
./scripts/test.sh

# Run documentation script
./scripts/docs.sh
```

## Docker Development

### Development Container

```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Install in development mode
RUN pip install -e ".[dev,docs,test]"

# Set default command
CMD ["bash"]
```

### Build and Run

```bash
# Build development image
docker build -f Dockerfile.dev -t llm-dispatcher-dev .

# Run development container
docker run -it --rm llm-dispatcher-dev

# Run with volume mount for live development
docker run -it --rm -v $(pwd):/app llm-dispatcher-dev
```

## Continuous Integration

### GitHub Actions

The project uses GitHub Actions for CI/CD. Workflows are defined in `.github/workflows/`:

- **CI**: Runs tests and linting
- **Release**: Builds and publishes packages
- **Documentation**: Builds and deploys documentation

### Local CI Simulation

```bash
# Run CI checks locally
./scripts/ci.sh

# Or run individual checks
./scripts/lint.sh
./scripts/test.sh
```

## Release Process

### 1. Update Version

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Update documentation
```

### 2. Create Release Branch

```bash
git checkout -b release/v0.1.0
```

### 3. Build and Test

```bash
# Clean previous builds
rm -rf dist/ build/

# Build package
python -m build

# Test built package
pip install dist/llm_dispatcher-*.whl
python -c "import llm_dispatcher; print('Import successful')"
```

### 4. Create Release

```bash
# Tag release
git tag v0.1.0
git push origin v0.1.0

# Create GitHub release
# Upload built packages
```

### 5. Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Upload to TestPyPI first
twine upload --repository testpypi dist/*
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Make sure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run specific test with debugging
pytest -v -s tests/test_specific.py::test_function

# Check test coverage
pytest --cov=llm_dispatcher --cov-report=term-missing
```

#### Build Failures

```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info/

# Reinstall build dependencies
pip install --upgrade build twine

# Check for syntax errors
python -m py_compile src/llm_dispatcher/*.py
```

#### Documentation Build Issues

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Check MkDocs configuration
mkdocs --version

# Build with verbose output
mkdocs build --verbose
```

### Getting Help

- Check the [Contributing Guide](contributing.md)
- Review [GitHub Issues](https://github.com/ashhadahsan/llm-dispatcher/issues)
- Join [Discord](https://discord.gg/llm-dispatcher)
- Email: support@llm-dispatcher.com

## Next Steps

- [:octicons-book-24: Contributing](contributing.md) - Contribution guidelines
- [:octicons-beaker-24: Testing](testing.md) - Testing guidelines and best practices
- [:octicons-shield-check-24: Security](security.md) - Security guidelines and reporting
- [:octicons-history-24: Changelog](changelog.md) - Project changelog and release notes
