"""
Pytest configuration and fixtures for LLM-Dispatcher tests.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import os
import asyncio
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_api_key():
    """Provide a mock OpenAI API key for testing."""
    return "sk-test1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def mock_anthropic_api_key():
    """Provide a mock Anthropic API key for testing."""
    return "sk-ant-test1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def mock_google_api_key():
    """Provide a mock Google API key for testing."""
    return "AIzaSyTest1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def real_openai_api_key():
    """Provide real OpenAI API key if available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        pytest.skip("Real OpenAI API key not available")
    return api_key


@pytest.fixture
def sample_task_request():
    """Provide a sample task request for testing."""
    from llm_dispatcher.core.base import TaskRequest, TaskType

    return TaskRequest(
        prompt="Write a simple Python function to add two numbers",
        task_type=TaskType.CODE_GENERATION,
        temperature=0.7,
        max_tokens=200,
    )


@pytest.fixture
def sample_vision_request():
    """Provide a sample vision task request for testing."""
    from llm_dispatcher.core.base import TaskRequest, TaskType

    return TaskRequest(
        prompt="Describe what you see in this image",
        task_type=TaskType.VISION_ANALYSIS,
        images=["base64_encoded_image_data"],
        temperature=0.3,
    )


@pytest.fixture
def sample_math_request():
    """Provide a sample math task request for testing."""
    from llm_dispatcher.core.base import TaskRequest, TaskType

    return TaskRequest(
        prompt="Solve the equation: 2x + 5 = 15",
        task_type=TaskType.MATH,
        temperature=0.1,
    )


@pytest.fixture
def sample_text_generation_request():
    """Provide a sample text generation request for testing."""
    from llm_dispatcher.core.base import TaskRequest, TaskType

    return TaskRequest(
        prompt="Write a short story about a robot learning to paint",
        task_type=TaskType.TEXT_GENERATION,
        temperature=0.8,
        max_tokens=300,
    )


@pytest.fixture
def mock_openai_response():
    """Provide a mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "This is a mock response from OpenAI"
    return mock_response


@pytest.fixture
def mock_openai_streaming_response():
    """Provide a mock OpenAI streaming response."""
    mock_chunks = [
        Mock(choices=[Mock(delta=Mock(content="Hello"))]),
        Mock(choices=[Mock(delta=Mock(content=" world"))]),
        Mock(choices=[Mock(delta=Mock(content="!"))]),
    ]

    async def mock_stream():
        for chunk in mock_chunks:
            yield chunk

    return mock_stream()


@pytest.fixture
def mock_embeddings_response():
    """Provide a mock embeddings response."""
    mock_response = Mock()
    mock_response.data = [Mock()]
    mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500 dimensions
    return mock_response


@pytest.fixture
def benchmark_manager():
    """Provide a benchmark manager instance for testing."""
    from llm_dispatcher.utils.benchmark_manager import BenchmarkManager

    return BenchmarkManager()


@pytest.fixture
def task_classifier():
    """Provide a task classifier instance for testing."""
    from llm_dispatcher.utils.task_classifier import TaskClassifier

    return TaskClassifier()


@pytest.fixture
def cost_calculator():
    """Provide a cost calculator instance for testing."""
    from llm_dispatcher.utils.cost_calculator import CostCalculator

    return CostCalculator()


@pytest.fixture
def performance_monitor():
    """Provide a performance monitor instance for testing."""
    from llm_dispatcher.utils.performance_monitor import PerformanceMonitor

    return PerformanceMonitor()


@pytest.fixture
def switch_config():
    """Provide a switch configuration instance for testing."""
    from llm_dispatcher.config.settings import SwitchConfig

    return SwitchConfig()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring real API keys"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "openai: mark test as requiring OpenAI API")
    config.addinivalue_line(
        "markers", "anthropic: mark test as requiring Anthropic API"
    )
    config.addinivalue_line("markers", "google: mark test as requiring Google API")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add integration marker to tests that require real API keys
        if "real_api" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.integration)

        # Add slow marker to tests that might be slow
        if "streaming" in item.name or "embeddings" in item.name:
            item.add_marker(pytest.mark.slow)

        # Add provider-specific markers
        if "openai" in item.name:
            item.add_marker(pytest.mark.openai)
        elif "anthropic" in item.name:
            item.add_marker(pytest.mark.anthropic)
        elif "google" in item.name:
            item.add_marker(pytest.mark.google)
