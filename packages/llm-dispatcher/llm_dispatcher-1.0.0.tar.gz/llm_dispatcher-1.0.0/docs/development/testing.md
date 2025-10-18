# Testing

Comprehensive testing guidelines and best practices for LLM-Dispatcher development.

## Current Test Status

**Test Coverage: 22%** (29/29 core tests passing) ✅

### Test Results Summary

| Test Category         | Tests | Status     | Coverage | Description                                    |
| --------------------- | ----- | ---------- | -------- | ---------------------------------------------- |
| **Core Tests**        | 27    | ✅ Passing | 98%      | Basic functionality, configurations, providers |
| **Performance Tests** | 1     | ✅ Passing | 37%      | Latency and throughput testing                 |
| **Benchmark Tests**   | 1     | ✅ Passing | 16%      | Metric calculations and validation             |

### Quick Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/llm_dispatcher --cov-report=html

# Run specific categories
pytest tests/test_basic.py                    # Core functionality
pytest tests/test_performance.py              # Performance tests
pytest tests/test_benchmark_utils.py          # Benchmark utilities
```

## Overview

Testing in LLM-Dispatcher includes:

- **Unit Tests** - Test individual components in isolation
- **Integration Tests** - Test component interactions
- **Performance Tests** - Test performance and scalability
- **End-to-End Tests** - Test complete workflows
- **Mock Testing** - Test with simulated external services
- **Property-Based Testing** - Test with generated inputs

## Test Structure

### Directory Organization

```
tests/
├── unit/                    # Unit tests
│   ├── test_providers/      # Provider unit tests
│   ├── test_core/          # Core functionality tests
│   ├── test_config/        # Configuration tests
│   └── test_utils/         # Utility function tests
├── integration/            # Integration tests
│   ├── test_provider_integration/
│   ├── test_workflow_integration/
│   └── test_api_integration/
├── performance/            # Performance tests
│   ├── test_benchmarks/
│   ├── test_load/
│   └── test_stress/
├── e2e/                    # End-to-end tests
│   ├── test_complete_workflows/
│   └── test_user_scenarios/
├── fixtures/               # Test fixtures and data
│   ├── mock_responses/
│   ├── test_data/
│   └── sample_configs/
└── conftest.py            # Pytest configuration
```

### Test Configuration

```python
# conftest.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from llm_dispatcher.core.base import TaskRequest, TaskType
from llm_dispatcher.providers.base_provider import LLMProvider

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_task_request():
    """Create a sample task request for testing."""
    return TaskRequest(
        prompt="Test prompt",
        task_type=TaskType.TEXT_GENERATION,
        max_tokens=100,
        temperature=0.7
    )

@pytest.fixture
def sample_task_response():
    """Create a sample task response for testing."""
    return TaskResponse(
        content="Test response",
        provider="test_provider",
        model="test_model",
        tokens_used=50,
        cost=0.001,
        latency=1000
    )

@pytest.fixture
def mock_provider_config():
    """Create a mock provider configuration."""
    return {
        "name": "test_provider",
        "api_key": "test_key",
        "models": ["test_model"],
        "max_tokens": 1000,
        "temperature": 0.7
    }

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage.total_tokens = 100
    mock_response.usage.prompt_tokens = 50
    mock_response.usage.completion_tokens = 50
    return mock_response

@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response."""
    mock_response = AsyncMock()
    mock_response.content = [AsyncMock()]
    mock_response.content[0].text = "Test response"
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 50
    return mock_response
```

## Unit Testing

### Provider Testing

```python
# tests/unit/test_providers/test_openai_provider.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from llm_dispatcher.providers.openai_provider import OpenAIProvider
from llm_dispatcher.core.base import TaskRequest, TaskType, TaskResponse
from llm_dispatcher.exceptions import ProviderError

class TestOpenAIProvider:
    """Test cases for OpenAI provider."""

    @pytest.fixture
    def provider(self, mock_provider_config):
        """Create OpenAI provider instance for testing."""
        return OpenAIProvider(mock_provider_config)

    @pytest.fixture
    def request(self, sample_task_request):
        """Create test request."""
        return sample_task_request

    @pytest.mark.asyncio
    async def test_generate_text_success(self, provider, request, mock_openai_response):
        """Test successful text generation."""
        with patch('llm_dispatcher.providers.openai_provider.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_openai_response

            result = await provider.generate_text(request)

            assert isinstance(result, TaskResponse)
            assert result.content == "Test response"
            assert result.provider == "test_provider"
            assert result.tokens_used == 100
            assert result.cost > 0
            assert result.latency > 0

    @pytest.mark.asyncio
    async def test_generate_text_failure(self, provider, request):
        """Test text generation failure."""
        with patch('llm_dispatcher.providers.openai_provider.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            with pytest.raises(ProviderError):
                await provider.generate_text(request)

    @pytest.mark.asyncio
    async def test_stream_text(self, provider, request):
        """Test streaming text generation."""
        with patch('llm_dispatcher.providers.openai_provider.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            # Mock streaming response
            mock_chunk = AsyncMock()
            mock_chunk.choices = [AsyncMock()]
            mock_chunk.choices[0].delta.content = "Test"
            mock_chunk.choices[0].finish_reason = None

            mock_client.chat.completions.create.return_value = [mock_chunk]

            chunks = []
            async for chunk in provider.stream_text(request):
                chunks.append(chunk)

            assert len(chunks) > 0
            assert chunks[0] == "Test"

    def test_get_cost_estimate(self, provider, request):
        """Test cost estimation."""
        cost = provider.get_cost_estimate(request)
        assert isinstance(cost, float)
        assert cost > 0

    def test_get_latency_estimate(self, provider, request):
        """Test latency estimation."""
        latency = provider.get_latency_estimate(request)
        assert isinstance(latency, int)
        assert latency > 0

    def test_is_healthy(self, provider):
        """Test health check."""
        assert provider.is_healthy() is True

    def test_get_available_models(self, provider):
        """Test getting available models."""
        models = provider.get_available_models()
        assert isinstance(models, list)
        assert "test_model" in models
```

### Core Functionality Testing

```python
# tests/unit/test_core/test_switch_engine.py
import pytest
from unittest.mock import AsyncMock, patch

from llm_dispatcher.core.switch_engine import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType
from llm_dispatcher.config.settings import OptimizationStrategy

class TestLLMSwitch:
    """Test cases for LLM switch engine."""

    @pytest.fixture
    def switch(self):
        """Create LLM switch instance for testing."""
        providers = {
            "openai": {
                "name": "openai",
                "api_key": "test_key",
                "models": ["gpt-4"]
            },
            "anthropic": {
                "name": "anthropic",
                "api_key": "test_key",
                "models": ["claude-3-sonnet"]
            }
        }
        return LLMSwitch(providers=providers)

    @pytest.fixture
    def request(self, sample_task_request):
        """Create test request."""
        return sample_task_request

    @pytest.mark.asyncio
    async def test_process_request_success(self, switch, request):
        """Test successful request processing."""
        with patch.object(switch.providers["openai"], 'generate_text') as mock_generate:
            mock_generate.return_value = AsyncMock()
            mock_generate.return_value.content = "Test response"

            result = await switch.process_request(request)

            assert result.content == "Test response"
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_request_with_fallback(self, switch, request):
        """Test request processing with fallback."""
        with patch.object(switch.providers["openai"], 'generate_text') as mock_openai:
            with patch.object(switch.providers["anthropic"], 'generate_text') as mock_anthropic:
                mock_openai.side_effect = Exception("OpenAI error")
                mock_anthropic.return_value = AsyncMock()
                mock_anthropic.return_value.content = "Fallback response"

                result = await switch.process_request(request)

                assert result.content == "Fallback response"
                mock_anthropic.assert_called_once()

    def test_get_provider_status(self, switch):
        """Test getting provider status."""
        status = switch.get_provider_status()
        assert isinstance(status, dict)
        assert "openai" in status
        assert "anthropic" in status

    def test_optimization_strategy(self, switch):
        """Test optimization strategy."""
        switch.config.optimization_strategy = OptimizationStrategy.COST
        assert switch.config.optimization_strategy == OptimizationStrategy.COST
```

## Integration Testing

### Provider Integration Tests

```python
# tests/integration/test_provider_integration.py
import pytest
import asyncio
from unittest.mock import patch

from llm_dispatcher import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType

class TestProviderIntegration:
    """Integration tests for providers."""

    @pytest.fixture
    def switch(self):
        """Create switch with real provider configurations."""
        return LLMSwitch(
            providers={
                "openai": {
                    "name": "openai",
                    "api_key": "test_key",
                    "models": ["gpt-4"]
                }
            }
        )

    @pytest.mark.asyncio
    async def test_openai_integration(self, switch):
        """Test OpenAI provider integration."""
        request = TaskRequest(
            prompt="Write a haiku about testing",
            task_type=TaskType.CREATIVE_WRITING
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            # Mock successful response
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Testing code with care,\nBugs vanish in the morning light,\nQuality software blooms."
            mock_response.usage.total_tokens = 50

            mock_client.chat.completions.create.return_value = mock_response

            result = await switch.process_request(request)

            assert result.content is not None
            assert len(result.content) > 0
            assert result.provider == "openai"

    @pytest.mark.asyncio
    async def test_anthropic_integration(self, switch):
        """Test Anthropic provider integration."""
        # Add Anthropic provider
        switch.providers["anthropic"] = {
            "name": "anthropic",
            "api_key": "test_key",
            "models": ["claude-3-sonnet"]
        }

        request = TaskRequest(
            prompt="Explain the concept of testing",
            task_type=TaskType.EXPLANATION
        )

        with patch('anthropic.AsyncAnthropic') as mock_anthropic:
            # Mock successful response
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.content = [AsyncMock()]
            mock_response.content[0].text = "Testing is the process of verifying that software works as expected."
            mock_response.usage.input_tokens = 20
            mock_response.usage.output_tokens = 30

            mock_client.messages.create.return_value = mock_response

            result = await switch.process_request(request)

            assert result.content is not None
            assert "testing" in result.content.lower()
            assert result.provider == "anthropic"
```

### Workflow Integration Tests

```python
# tests/integration/test_workflow_integration.py
import pytest
from unittest.mock import patch, AsyncMock

from llm_dispatcher import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType

class TestWorkflowIntegration:
    """Integration tests for complete workflows."""

    @pytest.fixture
    def switch(self):
        """Create switch for workflow testing."""
        return LLMSwitch(
            providers={
                "openai": {
                    "name": "openai",
                    "api_key": "test_key",
                    "models": ["gpt-4"]
                }
            },
            config={
                "optimization_strategy": "balanced",
                "fallback_enabled": True,
                "max_retries": 3
            }
        )

    @pytest.mark.asyncio
    async def test_complete_generation_workflow(self, switch):
        """Test complete text generation workflow."""
        request = TaskRequest(
            prompt="Write a short story about a robot learning to paint",
            task_type=TaskType.CREATIVE_WRITING,
            max_tokens=200
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Once upon a time, there was a robot named ArtBot who discovered the joy of painting..."
            mock_response.usage.total_tokens = 150

            mock_client.chat.completions.create.return_value = mock_response

            result = await switch.process_request(request)

            assert result.content is not None
            assert "robot" in result.content.lower()
            assert "painting" in result.content.lower()
            assert result.tokens_used == 150

    @pytest.mark.asyncio
    async def test_fallback_workflow(self, switch):
        """Test fallback workflow when primary provider fails."""
        # Add second provider
        switch.providers["anthropic"] = {
            "name": "anthropic",
            "api_key": "test_key",
            "models": ["claude-3-sonnet"]
        }

        request = TaskRequest(
            prompt="Explain quantum computing",
            task_type=TaskType.EXPLANATION
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            with patch('anthropic.AsyncAnthropic') as mock_anthropic:
                # Mock OpenAI failure
                mock_openai_client = AsyncMock()
                mock_openai.return_value = mock_openai_client
                mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API error")

                # Mock Anthropic success
                mock_anthropic_client = AsyncMock()
                mock_anthropic.return_value = mock_anthropic_client

                mock_response = AsyncMock()
                mock_response.content = [AsyncMock()]
                mock_response.content[0].text = "Quantum computing is a type of computation that uses quantum mechanical phenomena."
                mock_response.usage.input_tokens = 10
                mock_response.usage.output_tokens = 20

                mock_anthropic_client.messages.create.return_value = mock_response

                result = await switch.process_request(request)

                assert result.content is not None
                assert "quantum" in result.content.lower()
                assert result.provider == "anthropic"
```

## Performance Testing

### Benchmark Tests

```python
# tests/performance/test_benchmarks.py
import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock

from llm_dispatcher import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType

class TestPerformance:
    """Performance tests for LLM-Dispatcher."""

    @pytest.fixture
    def switch(self):
        """Create switch for performance testing."""
        return LLMSwitch(
            providers={
                "openai": {
                    "name": "openai",
                    "api_key": "test_key",
                    "models": ["gpt-4"]
                }
            }
        )

    @pytest.mark.asyncio
    async def test_latency_performance(self, switch):
        """Test latency performance."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 50

            mock_client.chat.completions.create.return_value = mock_response

            start_time = time.time()
            result = await switch.process_request(request)
            end_time = time.time()

            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            assert latency < 1000  # Should be under 1 second
            assert result.latency > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, switch):
        """Test concurrent request handling."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 50

            mock_client.chat.completions.create.return_value = mock_response

            # Create multiple concurrent requests
            tasks = [switch.process_request(request) for _ in range(10)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 10
            for result in results:
                assert result.content == "Test response"

    @pytest.mark.asyncio
    async def test_memory_usage(self, switch):
        """Test memory usage during operation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage.total_tokens = 50

            mock_client.chat.completions.create.return_value = mock_response

            # Process multiple requests
            for _ in range(100):
                await switch.process_request(request)

            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024
```

## Mock Testing

### Mock External Services

```python
# tests/unit/test_mocks.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from llm_dispatcher.providers.openai_provider import OpenAIProvider
from llm_dispatcher.core.base import TaskRequest, TaskType

class TestMocking:
    """Test cases for mocking external services."""

    @pytest.fixture
    def provider(self):
        """Create provider for mocking tests."""
        return OpenAIProvider({
            "name": "openai",
            "api_key": "test_key",
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
    async def test_mock_openai_api(self, provider, request):
        """Test mocking OpenAI API."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            # Configure mock
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Mocked response"
            mock_response.usage.total_tokens = 100

            mock_client.chat.completions.create.return_value = mock_response

            # Test the provider
            result = await provider.generate_text(request)

            # Verify mock was called correctly
            mock_openai.assert_called_once_with(api_key="test_key")
            mock_client.chat.completions.create.assert_called_once()

            # Verify result
            assert result.content == "Mocked response"
            assert result.tokens_used == 100

    @pytest.mark.asyncio
    async def test_mock_api_error(self, provider, request):
        """Test mocking API errors."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            # Mock API error
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

            with pytest.raises(Exception, match="Rate limit exceeded"):
                await provider.generate_text(request)

    @pytest.mark.asyncio
    async def test_mock_streaming(self, provider, request):
        """Test mocking streaming responses."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            # Mock streaming response
            mock_chunks = [
                AsyncMock(choices=[AsyncMock(delta=AsyncMock(content="Hello"))]),
                AsyncMock(choices=[AsyncMock(delta=AsyncMock(content=" world"))]),
                AsyncMock(choices=[AsyncMock(delta=AsyncMock(content="!"))])
            ]

            mock_client.chat.completions.create.return_value = mock_chunks

            chunks = []
            async for chunk in provider.stream_text(request):
                chunks.append(chunk)

            assert chunks == ["Hello", " world", "!"]
```

## Property-Based Testing

### Hypothesis Testing

```python
# tests/unit/test_property_based.py
import pytest
from hypothesis import given, strategies as st
from unittest.mock import patch, AsyncMock

from llm_dispatcher.providers.openai_provider import OpenAIProvider
from llm_dispatcher.core.base import TaskRequest, TaskType

class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @pytest.fixture
    def provider(self):
        """Create provider for property-based testing."""
        return OpenAIProvider({
            "name": "openai",
            "api_key": "test_key",
            "models": ["gpt-4"]
        })

    @given(st.text(min_size=1, max_size=1000))
    @pytest.mark.asyncio
    async def test_generate_text_with_any_prompt(self, provider, prompt):
        """Test text generation with any valid prompt."""
        request = TaskRequest(
            prompt=prompt,
            task_type=TaskType.TEXT_GENERATION
        )

        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = f"Response to: {prompt}"
            mock_response.usage.total_tokens = len(prompt.split())

            mock_client.chat.completions.create.return_value = mock_response

            result = await provider.generate_text(request)

            # Properties that should always hold
            assert result.content is not None
            assert len(result.content) > 0
            assert result.tokens_used > 0
            assert result.cost >= 0
            assert result.latency > 0
            assert result.provider == "openai"

    @given(st.integers(min_value=1, max_value=4000))
    def test_cost_estimate_with_any_token_count(self, provider, token_count):
        """Test cost estimation with any valid token count."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
            max_tokens=token_count
        )

        cost = provider.get_cost_estimate(request)

        # Properties that should always hold
        assert cost >= 0
        assert isinstance(cost, float)
        # Cost should increase with token count
        assert cost > 0 if token_count > 0 else cost == 0

    @given(st.floats(min_value=0.0, max_value=2.0))
    def test_temperature_validation(self, temperature):
        """Test temperature parameter validation."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
            temperature=temperature
        )

        # Temperature should be within valid range
        assert 0.0 <= temperature <= 2.0
```

## Test Utilities

### Custom Test Helpers

```python
# tests/utils/test_helpers.py
import pytest
import asyncio
from typing import List, Dict, Any
from unittest.mock import AsyncMock

from llm_dispatcher.core.base import TaskRequest, TaskResponse, TaskType

class TestHelpers:
    """Helper functions for testing."""

    @staticmethod
    def create_mock_response(content: str, tokens: int = 100) -> AsyncMock:
        """Create a mock response for testing."""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = content
        mock_response.usage.total_tokens = tokens
        return mock_response

    @staticmethod
    def create_test_request(
        prompt: str = "Test prompt",
        task_type: TaskType = TaskType.TEXT_GENERATION,
        **kwargs
    ) -> TaskRequest:
        """Create a test request with default values."""
        return TaskRequest(
            prompt=prompt,
            task_type=task_type,
            **kwargs
        )

    @staticmethod
    async def run_concurrent_requests(
        switch,
        request: TaskRequest,
        count: int = 10
    ) -> List[TaskResponse]:
        """Run multiple concurrent requests for testing."""
        tasks = [switch.process_request(request) for _ in range(count)]
        return await asyncio.gather(*tasks)

    @staticmethod
    def assert_response_valid(response: TaskResponse) -> None:
        """Assert that a response is valid."""
        assert response.content is not None
        assert len(response.content) > 0
        assert response.tokens_used > 0
        assert response.cost >= 0
        assert response.latency > 0
        assert response.provider is not None
        assert response.model is not None

# Usage in tests
class TestWithHelpers:
    """Test class using helper functions."""

    def test_with_helpers(self):
        """Test using helper functions."""
        request = TestHelpers.create_test_request("Test prompt")
        mock_response = TestHelpers.create_mock_response("Test response", 50)

        assert request.prompt == "Test prompt"
        assert mock_response.usage.total_tokens == 50
```

## Running Tests

### Test Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_openai_provider.py

# Run tests with coverage
pytest --cov=llm_dispatcher --cov-report=html

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only performance tests
pytest tests/performance/

# Run tests matching pattern
pytest -k "test_openai"

# Run tests with specific marker
pytest -m "not slow"

# Run tests with coverage and fail under threshold
pytest --cov=llm_dispatcher --cov-fail-under=80
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=llm_dispatcher
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    unit: marks tests as unit tests
asyncio_mode = auto
```

## Best Practices

### 1. **Write Clear Test Names**

```python
# Good: Clear, descriptive test names
def test_generate_text_returns_valid_response():
    """Test that text generation returns a valid response."""
    pass

def test_provider_handles_api_errors_gracefully():
    """Test that provider handles API errors gracefully."""
    pass

# Avoid: Unclear test names
def test_provider():
    """Test provider."""
    pass

def test_1():
    """Test 1."""
    pass
```

### 2. **Use Appropriate Test Scope**

```python
# Good: Test one thing at a time
def test_generate_text_success():
    """Test successful text generation."""
    pass

def test_generate_text_failure():
    """Test text generation failure."""
    pass

# Avoid: Testing multiple things in one test
def test_provider_everything():
    """Test everything about provider."""
    pass
```

### 3. **Mock External Dependencies**

```python
# Good: Mock external dependencies
@patch('openai.AsyncOpenAI')
def test_generate_text(mock_openai):
    """Test text generation with mocked OpenAI."""
    pass

# Avoid: Making real API calls in tests
def test_generate_text():
    """Test text generation with real API."""
    # This will make real API calls
    pass
```

### 4. **Use Fixtures for Common Setup**

```python
# Good: Use fixtures for common setup
@pytest.fixture
def provider():
    """Create provider for testing."""
    return OpenAIProvider({"api_key": "test"})

def test_something(provider):
    """Test using provider fixture."""
    pass

# Avoid: Repeating setup code
def test_something():
    """Test with repeated setup."""
    provider = OpenAIProvider({"api_key": "test"})
    # ... test code
```

### 5. **Test Edge Cases**

```python
# Good: Test edge cases
def test_empty_prompt():
    """Test handling of empty prompt."""
    pass

def test_very_long_prompt():
    """Test handling of very long prompt."""
    pass

def test_invalid_parameters():
    """Test handling of invalid parameters."""
    pass

# Avoid: Only testing happy path
def test_normal_case():
    """Test normal case only."""
    pass
```

## Next Steps

- [:octicons-book-24: Contributing](contributing.md) - Contribution guidelines
- [:octicons-history-24: Changelog](changelog.md) - Project changelog and release notes
- [:octicons-shield-check-24: Security](security.md) - Security guidelines and reporting
- [:octicons-beaker-24: Code of Conduct](code-of-conduct.md) - Community guidelines
