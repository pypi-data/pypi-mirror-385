"""
Comprehensive tests for Google provider.

This module contains tests for the Google provider implementation,
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

from llm_dispatcher.providers.google_provider import GoogleProvider
from llm_dispatcher.core.base import (
    TaskRequest,
    TaskResponse,
    TaskType,
    Capability,
    ModelInfo,
    PerformanceMetrics,
)


class TestGoogleProvider:
    """Test the Google provider implementation."""

    @pytest.fixture
    def mock_google_client(self):
        """Create a mock Google client."""
        with patch("llm_dispatcher.providers.google_provider.GenerativeModel") as mock:
            model_instance = AsyncMock()
            mock.return_value = model_instance
            yield model_instance

    @pytest.fixture
    def provider(self, mock_google_client):
        """Create a test Google provider instance."""
        api_key = os.getenv("GOOGLE_API_KEY", "test_api_key")
        return GoogleProvider(api_key=api_key)

    def test_provider_initialization(self, provider):
        """Test Google provider initialization."""
        assert provider is not None
        assert provider.provider_name == "google"
        assert provider.api_key is not None
        assert len(provider.models) > 0

    def test_models_initialization(self, provider):
        """Test that models are properly initialized."""
        expected_models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
            "gemini-1.5-pro-latest",
        ]

        for model_name in expected_models:
            if model_name in provider.models:  # Some models might not be available
                model_info = provider.models[model_name]
                assert isinstance(model_info, ModelInfo)
                assert model_info.name == model_name
                assert model_info.provider == "google"

    def test_model_capabilities(self, provider):
        """Test model capabilities are correctly set."""
        # Test Gemini Pro capabilities
        if "gemini-1.5-pro" in provider.models:
            gemini_info = provider.models["gemini-1.5-pro"]
            assert Capability.TEXT in gemini_info.capabilities
            assert Capability.VISION in gemini_info.capabilities
            assert Capability.STRUCTURED_OUTPUT in gemini_info.capabilities

    def test_benchmark_scores(self, provider):
        """Test that benchmark scores are properly set."""
        if "gemini-1.5-pro" in provider.models:
            gemini_info = provider.models["gemini-1.5-pro"]
            scores = gemini_info.benchmark_scores

            assert "mmlu" in scores
            assert "human_eval" in scores
            assert scores["mmlu"] > 0.7  # Gemini should have good scores

    def test_cost_per_tokens(self, provider):
        """Test cost calculation per tokens."""
        if "gemini-1.5-pro" in provider.models:
            gemini_info = provider.models["gemini-1.5-pro"]
            cost_info = gemini_info.cost_per_1k_tokens

            assert "input" in cost_info
            assert "output" in cost_info
            assert cost_info["input"] > 0
            assert cost_info["output"] > 0

    @pytest.mark.asyncio
    async def test_generate_basic(self, provider, mock_google_client):
        """Test basic text generation."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Test response from Gemini"
        mock_response.usage_metadata = Mock(
            prompt_token_count=10, candidates_token_count=5, total_token_count=15
        )

        mock_google_client.generate_content = AsyncMock(return_value=mock_response)

        # Create a test request
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test generation
        response = await provider.generate(request, "gemini-1.5-pro")

        assert isinstance(response, TaskResponse)
        assert response.content == "Test response from Gemini"
        assert response.model_used == "gemini-1.5-pro"
        assert response.provider == "google"

    @pytest.mark.asyncio
    async def test_generate_with_vision(self, provider, mock_google_client):
        """Test generation with vision capability."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "I can see the image"
        mock_response.usage_metadata = Mock(
            prompt_token_count=15, candidates_token_count=5, total_token_count=20
        )

        mock_google_client.generate_content = AsyncMock(return_value=mock_response)

        # Create a request with image
        request = TaskRequest(
            prompt="Describe this image",
            task_type=TaskType.VISION_ANALYSIS,
            images=["base64_image_data"],
        )

        response = await provider.generate(request, "gemini-1.5-pro")

        assert response.content == "I can see the image"

    @pytest.mark.asyncio
    async def test_generate_with_structured_output(self, provider, mock_google_client):
        """Test generation with structured output."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = '{"name": "test", "value": 123}'
        mock_response.usage_metadata = Mock(
            prompt_token_count=10, candidates_token_count=10, total_token_count=20
        )

        mock_google_client.generate_content = AsyncMock(return_value=mock_response)

        # Create a request with structured output
        request = TaskRequest(
            prompt="Generate a JSON object",
            task_type=TaskType.TEXT_GENERATION,
            structured_output={"type": "json_object"},
        )

        response = await provider.generate(request, "gemini-1.5-pro")

        assert response.content == '{"name": "test", "value": 123}'

    @pytest.mark.asyncio
    async def test_generate_streaming(self, provider, mock_google_client):
        """Test streaming generation."""

        # Mock the streaming response
        async def mock_stream():
            chunk1 = Mock()
            chunk1.text = "Hello"
            yield chunk1

            chunk2 = Mock()
            chunk2.text = " world"
            yield chunk2

        mock_google_client.generate_content_stream = AsyncMock(
            return_value=mock_stream()
        )

        # Create a test request
        request = TaskRequest(
            prompt="Say hello world",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test streaming generation
        chunks = []
        async for chunk in provider.generate_stream(request, "gemini-1.5-pro"):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0] == "Hello"
        assert chunks[1] == " world"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, provider, mock_google_client):
        """Test handling of API errors."""
        # Mock an API error
        from google.api_core import exceptions as google_exceptions

        mock_google_client.generate_content = AsyncMock(
            side_effect=google_exceptions.InvalidArgument("Invalid argument")
        )

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test that the error is properly handled
        with pytest.raises(RuntimeError, match="Google API call failed"):
            await provider.generate(request, "gemini-1.5-pro")

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
        if "gemini-1.5-pro" in provider.models:
            cost = provider.estimate_cost("gemini-1.5-pro", 100, 50)
            assert cost > 0

    def test_get_model_info(self, provider):
        """Test getting model information."""
        if "gemini-1.5-pro" in provider.models:
            model_info = provider.get_model_info("gemini-1.5-pro")
            assert isinstance(model_info, ModelInfo)
            assert model_info.name == "gemini-1.5-pro"

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


class TestGoogleProviderIntegration:
    """Integration tests for Google provider with real API (if API key is available)."""

    @pytest.fixture
    def real_provider(self):
        """Create a real Google provider instance if API key is available."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_google_api_key_here":
            pytest.skip("Google API key not available for integration tests")
        return GoogleProvider(api_key=api_key)

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
        assert response.provider == "google"

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
