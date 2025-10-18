"""
Comprehensive tests for Grok provider.

This module contains tests for the Grok provider implementation,
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

from llm_dispatcher.providers.grok_provider import GrokProvider
from llm_dispatcher.core.base import (
    TaskRequest,
    TaskResponse,
    TaskType,
    Capability,
    ModelInfo,
    PerformanceMetrics,
)


class TestGrokProvider:
    """Test the Grok provider implementation."""

    @pytest.fixture
    def mock_grok_client(self):
        """Create a mock Grok client."""
        with patch("llm_dispatcher.providers.grok_provider.Grok") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def provider(self, mock_grok_client):
        """Create a test Grok provider instance."""
        api_key = os.getenv("GROK_API_KEY", "test_api_key")
        return GrokProvider(api_key=api_key)

    def test_provider_initialization(self, provider):
        """Test Grok provider initialization."""
        assert provider is not None
        assert provider.provider_name == "grok"
        assert provider.api_key is not None
        assert len(provider.models) > 0

    def test_models_initialization(self, provider):
        """Test that models are properly initialized."""
        expected_models = [
            "grok-3-beta",
            "grok-2",
        ]

        for model_name in expected_models:
            if model_name in provider.models:  # Some models might not be available
                model_info = provider.models[model_name]
                assert isinstance(model_info, ModelInfo)
                assert model_info.name == model_name
                assert model_info.provider == "grok"

    def test_model_capabilities(self, provider):
        """Test model capabilities are correctly set."""
        # Test Grok capabilities
        if "grok-3-beta" in provider.models:
            grok_info = provider.models["grok-3-beta"]
            assert Capability.TEXT in grok_info.capabilities
            assert Capability.VISION in grok_info.capabilities

    def test_benchmark_scores(self, provider):
        """Test that benchmark scores are properly set."""
        if "grok-3-beta" in provider.models:
            grok_info = provider.models["grok-3-beta"]
            scores = grok_info.benchmark_scores

            assert "mmlu" in scores
            assert "human_eval" in scores
            assert scores["mmlu"] > 0.5  # Grok should have decent scores

    def test_cost_per_tokens(self, provider):
        """Test cost calculation per tokens."""
        if "grok-3-beta" in provider.models:
            grok_info = provider.models["grok-3-beta"]
            cost_info = grok_info.cost_per_1k_tokens

            assert "input" in cost_info
            assert "output" in cost_info
            assert cost_info["input"] > 0
            assert cost_info["output"] > 0

    @pytest.mark.asyncio
    async def test_generate_basic(self, provider, mock_grok_client):
        """Test basic text generation."""
        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response from Grok"))]
        mock_response.usage = Mock(
            prompt_tokens=10, completion_tokens=5, total_tokens=15
        )

        mock_grok_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Create a test request
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test generation
        response = await provider.generate(request, "grok-3-beta")

        assert isinstance(response, TaskResponse)
        assert response.content == "Test response from Grok"
        assert response.model_used == "grok-3-beta"
        assert response.provider == "grok"

    @pytest.mark.asyncio
    async def test_generate_with_vision(self, provider, mock_grok_client):
        """Test generation with vision capability."""
        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="I can see the image"))]
        mock_response.usage = Mock(
            prompt_tokens=15, completion_tokens=5, total_tokens=20
        )

        mock_grok_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Create a request with image
        request = TaskRequest(
            prompt="Describe this image",
            task_type=TaskType.VISION_ANALYSIS,
            images=["base64_image_data"],
        )

        response = await provider.generate(request, "grok-3-beta")

        assert response.content == "I can see the image"

    @pytest.mark.asyncio
    async def test_generate_streaming(self, provider, mock_grok_client):
        """Test streaming generation."""

        # Mock the streaming response
        async def mock_stream():
            chunk1 = Mock()
            chunk1.choices = [Mock(delta=Mock(content="Hello"))]
            yield chunk1

            chunk2 = Mock()
            chunk2.choices = [Mock(delta=Mock(content=" world"))]
            yield chunk2

        mock_grok_client.chat.completions.create = AsyncMock(return_value=mock_stream())

        # Create a test request
        request = TaskRequest(
            prompt="Say hello world",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test streaming generation
        chunks = []
        async for chunk in provider.generate_stream(request, "grok-3-beta"):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0] == "Hello"
        assert chunks[1] == " world"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, provider, mock_grok_client):
        """Test handling of API errors."""
        # Mock an API error
        from groq import BadRequestError

        mock_grok_client.chat.completions.create = AsyncMock(
            side_effect=BadRequestError("API Error", response=Mock(), body={})
        )

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test that the error is properly handled
        with pytest.raises(RuntimeError, match="Grok API call failed"):
            await provider.generate(request, "grok-3-beta")

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
        if "grok-3-beta" in provider.models:
            cost = provider.estimate_cost("grok-3-beta", 100, 50)
            assert cost > 0

    def test_get_model_info(self, provider):
        """Test getting model information."""
        if "grok-3-beta" in provider.models:
            model_info = provider.get_model_info("grok-3-beta")
            assert isinstance(model_info, ModelInfo)
            assert model_info.name == "grok-3-beta"

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


class TestGrokProviderIntegration:
    """Integration tests for Grok provider with real API (if API key is available)."""

    @pytest.fixture
    def real_provider(self):
        """Create a real Grok provider instance if API key is available."""
        api_key = os.getenv("GROK_API_KEY")
        if not api_key or api_key == "your_grok_api_key_here":
            pytest.skip("Grok API key not available for integration tests")
        return GrokProvider(api_key=api_key)

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
        assert response.provider == "grok"

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
