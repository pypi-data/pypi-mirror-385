"""
Comprehensive tests for Anthropic provider.

This module contains tests for the Anthropic provider implementation,
including API calls, model selection, cost estimation, and error handling.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from llm_dispatcher.providers.anthropic_provider import AnthropicProvider
from llm_dispatcher.core.base import (
    TaskRequest,
    TaskResponse,
    TaskType,
    Capability,
    ModelInfo,
    PerformanceMetrics,
)


class TestAnthropicProvider:
    """Test the Anthropic provider implementation."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        with patch(
            "llm_dispatcher.providers.anthropic_provider.AsyncAnthropic"
        ) as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def provider(self, mock_anthropic_client):
        """Create a test Anthropic provider instance."""
        api_key = os.getenv("ANTHROPIC_API_KEY", "test_api_key")
        return AnthropicProvider(api_key=api_key)

    def test_provider_initialization(self, provider):
        """Test Anthropic provider initialization."""
        assert provider is not None
        assert provider.provider_name == "anthropic"
        assert provider.api_key is not None
        assert len(provider.models) > 0

    def test_models_initialization(self, provider):
        """Test that models are properly initialized."""
        expected_models = [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
        ]

        for model_name in expected_models:
            if model_name in provider.models:  # Some models might not be available
                model_info = provider.models[model_name]
                assert isinstance(model_info, ModelInfo)
                # The model name should be the actual API model name, not the key
                assert (
                    model_info.name != model_name
                )  # API names are different from keys
                assert model_info.provider == "anthropic"

    def test_model_capabilities(self, provider):
        """Test model capabilities are correctly set."""
        # Test Claude 3 Opus capabilities
        if "claude-3-opus" in provider.models:
            claude_info = provider.models["claude-3-opus"]
            assert Capability.TEXT in claude_info.capabilities
            assert Capability.VISION in claude_info.capabilities
            assert Capability.STRUCTURED_OUTPUT in claude_info.capabilities

    def test_benchmark_scores(self, provider):
        """Test that benchmark scores are properly set."""
        if "claude-3-opus" in provider.models:
            claude_info = provider.models["claude-3-opus"]
            scores = claude_info.benchmark_scores

            assert "mmlu" in scores
            assert "human_eval" in scores
            assert scores["mmlu"] > 0.8  # Claude should have high scores

    def test_cost_per_tokens(self, provider):
        """Test cost calculation per tokens."""
        if "claude-3-opus" in provider.models:
            claude_info = provider.models["claude-3-opus"]
            cost_info = claude_info.cost_per_1k_tokens

            assert "input" in cost_info
            assert "output" in cost_info
            assert cost_info["input"] > 0
            assert cost_info["output"] > 0

    @pytest.mark.asyncio
    async def test_generate_basic(self, provider, mock_anthropic_client):
        """Test basic text generation."""
        # Mock the response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Test response from Claude"
        mock_content.type = "text"
        mock_response.content = [mock_content]
        mock_response.usage = Mock(input_tokens=10, output_tokens=5)

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        # Create a test request
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test generation
        response = await provider.generate(request, "claude-3-opus")

        assert isinstance(response, TaskResponse)
        assert response.content == "Test response from Claude"
        assert response.model_used == "claude-3-opus"
        assert response.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_generate_with_vision(self, provider, mock_anthropic_client):
        """Test generation with vision capability."""
        # Mock the response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "I can see the image"
        mock_content.type = "text"
        mock_response.content = [mock_content]
        mock_response.usage = Mock(input_tokens=15, output_tokens=5)

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        # Create a request with image
        request = TaskRequest(
            prompt="Describe this image",
            task_type=TaskType.VISION_ANALYSIS,
            images=["base64_image_data"],
        )

        response = await provider.generate(request, "claude-3-opus")

        assert response.content == "I can see the image"

    @pytest.mark.asyncio
    async def test_generate_with_structured_output(
        self, provider, mock_anthropic_client
    ):
        """Test generation with structured output."""
        # Mock the response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '{"name": "test", "value": 123}'
        mock_content.type = "text"
        mock_response.content = [mock_content]
        mock_response.usage = Mock(input_tokens=10, output_tokens=10)

        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        # Create a request with structured output
        request = TaskRequest(
            prompt="Generate a JSON object",
            task_type=TaskType.TEXT_GENERATION,
            structured_output={"type": "json_object"},
        )

        response = await provider.generate(request, "claude-3-opus")

        assert response.content == '{"name": "test", "value": 123}'

    @pytest.mark.asyncio
    async def test_generate_streaming(self, provider, mock_anthropic_client):
        """Test streaming generation."""

        # Mock the streaming response
        async def mock_stream():
            yield "Hello"
            yield " world"

        # Create a mock stream object with text_stream attribute
        mock_stream_obj = Mock()
        mock_stream_obj.text_stream = mock_stream()

        # Create a mock async context manager
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_stream_obj)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_anthropic_client.messages.stream = Mock(return_value=mock_context_manager)

        # Create a test request
        request = TaskRequest(
            prompt="Say hello world",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test streaming generation
        chunks = []
        async for chunk in provider.generate_stream(request, "claude-3-opus"):
            chunks.append(chunk)

        assert len(chunks) == 2  # Two content chunks
        assert chunks[0] == "Hello"
        assert chunks[1] == " world"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, provider, mock_anthropic_client):
        """Test handling of API errors."""
        # Mock an API error
        from anthropic import APIError

        mock_anthropic_client.messages.create = AsyncMock(
            side_effect=APIError("API Error", request=None, body=None)
        )

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test that the error is properly handled
        from llm_dispatcher.exceptions import ProviderConnectionError

        with pytest.raises(ProviderConnectionError, match="Unexpected error"):
            await provider.generate(request, "claude-3-opus")

    def test_get_models_for_task(self, provider):
        """Test getting models suitable for a specific task."""
        text_models = provider.get_models_for_task(TaskType.TEXT_GENERATION)
        assert isinstance(text_models, list)
        assert len(text_models) > 0

        vision_models = provider.get_models_for_task(TaskType.VISION_ANALYSIS)
        assert isinstance(vision_models, list)

    def test_get_best_model_for_task(self, provider):
        """Test getting the best model for a task."""
        best_model = provider.get_best_model_for_task(TaskType.TEXT_GENERATION)
        assert best_model is not None
        assert best_model in provider.models

    def test_estimate_cost(self, provider):
        """Test cost estimation."""
        if "claude-3-opus" in provider.models:
            cost = provider.estimate_cost("claude-3-opus", 100, 50)
            assert cost > 0

    def test_get_model_info(self, provider):
        """Test getting model information."""
        if "claude-3-opus" in provider.models:
            model_info = provider.get_model_info("claude-3-opus")
            assert isinstance(model_info, ModelInfo)
            # The model name should be the actual API model name, not the key
            assert (
                model_info.name != "claude-3-opus"
            )  # API names are different from keys

    def test_health_check(self, provider):
        """Test provider health status."""
        health = provider.get_health_status()
        assert isinstance(health, dict)
        assert "status" in health

    def test_statistics(self, provider):
        """Test provider statistics."""
        stats = provider.get_statistics()
        assert isinstance(stats, dict)
        assert "provider" in stats
        assert "total_requests" in stats


class TestAnthropicProviderIntegration:
    """Integration tests for Anthropic provider with real API (if API key is available)."""

    @pytest.fixture
    def real_provider(self):
        """Create a real Anthropic provider instance if API key is available."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_anthropic_api_key_here":
            pytest.skip("Anthropic API key not available for integration tests")
        return AnthropicProvider(api_key=api_key)

    @pytest.mark.asyncio
    async def test_real_api_call(self, real_provider):
        """Test real API call (requires valid API key)."""
        request = TaskRequest(
            prompt="Say hello in one word",
            task_type=TaskType.TEXT_GENERATION,
            max_tokens=10,
        )

        # Use the first available model
        model = list(real_provider.models.keys())[0]
        response = await real_provider.generate(request, model)

        assert isinstance(response, TaskResponse)
        assert response.content is not None
        assert len(response.content) > 0
        assert response.model_used == model
        assert response.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_real_streaming_call(self, real_provider):
        """Test real streaming API call (requires valid API key)."""
        request = TaskRequest(
            prompt="Count from 1 to 3",
            task_type=TaskType.TEXT_GENERATION,
            max_tokens=20,
        )

        # Use the first available model
        model = list(real_provider.models.keys())[0]
        chunks = []
        async for chunk in real_provider.generate_stream(request, model):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
