"""
Comprehensive tests for OpenAI provider.

This module contains tests for the OpenAI provider implementation,
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

from llm_dispatcher.providers.openai_provider import OpenAIProvider
from llm_dispatcher.core.base import (
    TaskRequest,
    TaskResponse,
    TaskType,
    Capability,
    ModelInfo,
    PerformanceMetrics,
)


class TestOpenAIProvider:
    """Test the OpenAI provider implementation."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch("llm_dispatcher.providers.openai_provider.AsyncOpenAI") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def provider(self, mock_openai_client):
        """Create a test OpenAI provider instance."""
        api_key = os.getenv("OPENAI_API_KEY", "test_api_key")
        return OpenAIProvider(api_key=api_key)

    def test_provider_initialization(self, provider):
        """Test OpenAI provider initialization."""
        assert provider is not None
        assert provider.provider_name == "openai"
        assert provider.api_key is not None
        assert len(provider.models) > 0

    def test_models_initialization(self, provider):
        """Test that models are properly initialized."""
        expected_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ]

        for model_name in expected_models:
            assert model_name in provider.models
            model_info = provider.models[model_name]
            assert isinstance(model_info, ModelInfo)
            assert model_info.name == model_name
            assert model_info.provider == "openai"

    def test_model_capabilities(self, provider):
        """Test model capabilities are correctly set."""
        # Test GPT-4 capabilities
        gpt4_info = provider.models["gpt-4"]
        assert Capability.TEXT in gpt4_info.capabilities
        assert Capability.VISION in gpt4_info.capabilities
        assert Capability.FUNCTION_CALLING in gpt4_info.capabilities
        assert Capability.STRUCTURED_OUTPUT in gpt4_info.capabilities

        # Test GPT-4o audio capability
        gpt4o_info = provider.models["gpt-4o"]
        assert Capability.AUDIO in gpt4o_info.capabilities

        # Test GPT-3.5-turbo (no vision/audio)
        gpt35_info = provider.models["gpt-3.5-turbo"]
        assert Capability.VISION not in gpt35_info.capabilities
        assert Capability.AUDIO not in gpt35_info.capabilities

    def test_benchmark_scores(self, provider):
        """Test that benchmark scores are properly set."""
        gpt4_info = provider.models["gpt-4"]
        scores = gpt4_info.benchmark_scores

        assert "mmlu" in scores
        assert "human_eval" in scores
        assert "gpqa" in scores
        assert "aime" in scores
        assert scores["mmlu"] > 0.8  # GPT-4 should have high MMLU score

    def test_cost_per_tokens(self, provider):
        """Test cost per token information."""
        gpt4_info = provider.models["gpt-4"]
        cost_info = gpt4_info.cost_per_1k_tokens

        assert "input" in cost_info
        assert "output" in cost_info
        assert cost_info["input"] > 0
        assert cost_info["output"] > 0

    def test_get_models_for_task(self, provider):
        """Test getting models suitable for specific tasks."""
        # Test code generation
        code_models = provider.get_models_for_task(TaskType.CODE_GENERATION)
        assert len(code_models) > 0
        assert all(model in provider.models for model in code_models)

        # Test vision analysis
        vision_models = provider.get_models_for_task(TaskType.VISION_ANALYSIS)
        assert len(vision_models) > 0
        # Should only include models with vision capability
        for model in vision_models:
            assert Capability.VISION in provider.models[model].capabilities

        # Test math tasks
        math_models = provider.get_models_for_task(TaskType.MATH)
        assert len(math_models) > 0

    def test_get_best_model_for_task(self, provider):
        """Test getting the best model for a task."""
        best_code_model = provider.get_best_model_for_task(TaskType.CODE_GENERATION)
        assert best_code_model is not None
        assert best_code_model in provider.models

        best_vision_model = provider.get_best_model_for_task(TaskType.VISION_ANALYSIS)
        assert best_vision_model is not None
        assert Capability.VISION in provider.models[best_vision_model].capabilities

    def test_performance_score_calculation(self, provider):
        """Test performance score calculation for different tasks."""
        # Test code generation score
        gpt4_code_score = provider.get_performance_score(
            "gpt-4", TaskType.CODE_GENERATION
        )
        assert gpt4_code_score > 0
        assert gpt4_code_score <= 1.0

        # Test math score
        gpt4_math_score = provider.get_performance_score("gpt-4", TaskType.MATH)
        assert gpt4_math_score > 0
        assert gpt4_math_score <= 1.0

        # Test vision score
        gpt4_vision_score = provider.get_performance_score(
            "gpt-4", TaskType.VISION_ANALYSIS
        )
        assert gpt4_vision_score > 0
        assert gpt4_vision_score <= 1.0

    def test_cost_estimation(self, provider):
        """Test cost estimation functionality."""
        # Test cost estimation for a model
        cost = provider.estimate_cost("gpt-4", 1000, 500)
        assert cost > 0

        # Test cost comparison between models
        gpt4_cost = provider.estimate_cost("gpt-4", 1000, 500)
        gpt35_cost = provider.estimate_cost("gpt-3.5-turbo", 1000, 500)

        # GPT-4 should be more expensive than GPT-3.5
        assert gpt4_cost > gpt35_cost

    def test_get_cost_estimate_for_task(self, provider):
        """Test getting cost estimates for all models for a task."""
        estimates = provider.get_cost_estimate(TaskType.TEXT_GENERATION, 1000, 500)

        assert isinstance(estimates, dict)
        assert len(estimates) > 0

        for model, cost in estimates.items():
            assert model in provider.models
            assert cost >= 0

    def test_performance_ranking(self, provider):
        """Test performance ranking for tasks."""
        rankings = provider.get_performance_ranking(TaskType.CODE_GENERATION)

        assert isinstance(rankings, list)
        assert len(rankings) > 0

        # Check that rankings are sorted (highest first)
        for i in range(len(rankings) - 1):
            assert rankings[i][1] >= rankings[i + 1][1]

    def test_token_estimation(self, provider):
        """Test token estimation functionality."""
        text = "This is a test prompt for token estimation."
        estimated_tokens = provider.estimate_tokens(text)

        assert estimated_tokens > 0
        assert isinstance(estimated_tokens, int)

    def test_model_info_retrieval(self, provider):
        """Test model information retrieval."""
        gpt4_info = provider.get_model_info("gpt-4")
        assert gpt4_info is not None
        assert gpt4_info.name == "gpt-4"
        assert gpt4_info.provider == "openai"

        # Test non-existent model
        non_existent = provider.get_model_info("non-existent-model")
        assert non_existent is None

    def test_performance_metrics_retrieval(self, provider):
        """Test performance metrics retrieval."""
        gpt4_metrics = provider.get_performance_metrics("gpt-4")
        assert gpt4_metrics is not None
        assert isinstance(gpt4_metrics, PerformanceMetrics)
        assert gpt4_metrics.mmlu_score is not None

        # Test non-existent model
        non_existent = provider.get_performance_metrics("non-existent-model")
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_generate_success(self, provider, mock_openai_client):
        """Test successful text generation."""
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "This is a test response"

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Create a test request
        request = TaskRequest(
            prompt="Test prompt", task_type=TaskType.TEXT_GENERATION, temperature=0.7
        )

        # Test generation
        response = await provider.generate(request, "gpt-4")

        assert isinstance(response, TaskResponse)
        assert response.content == "This is a test response"
        assert response.model_used == "gpt-4"
        assert response.provider == "openai"

    @pytest.mark.asyncio
    async def test_generate_with_structured_output(self, provider, mock_openai_client):
        """Test generation with structured output."""
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"result": "test"}'

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Create a test request with structured output
        request = TaskRequest(
            prompt="Generate a JSON response",
            task_type=TaskType.TEXT_GENERATION,
            structured_output=True,
        )

        # Test generation
        response = await provider.generate(request, "gpt-4")

        assert response.content == '{"result": "test"}'
        # Verify that response_format was set in the API call
        call_args = mock_openai_client.chat.completions.create.call_args
        assert "response_format" in call_args[1]

    @pytest.mark.asyncio
    async def test_generate_with_functions(self, provider, mock_openai_client):
        """Test generation with function calling."""
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Function call result"

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Create a test request with functions
        functions = [
            {
                "name": "test_function",
                "description": "A test function",
                "parameters": {
                    "type": "object",
                    "properties": {"param1": {"type": "string"}},
                },
            }
        ]

        request = TaskRequest(
            prompt="Call the test function",
            task_type=TaskType.FUNCTION_CALLING,
            functions=functions,
        )

        # Test generation
        response = await provider.generate(request, "gpt-4")

        assert response.content == "Function call result"
        # Verify that functions were passed to the API call
        call_args = mock_openai_client.chat.completions.create.call_args
        assert "functions" in call_args[1]
        assert "function_call" in call_args[1]

    @pytest.mark.asyncio
    async def test_generate_with_images(self, provider, mock_openai_client):
        """Test generation with image input."""
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Image analysis result"

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Create a test request with images
        request = TaskRequest(
            prompt="Analyze this image",
            task_type=TaskType.VISION_ANALYSIS,
            images=["base64_encoded_image_data"],
        )

        # Test generation
        response = await provider.generate(request, "gpt-4")

        assert response.content == "Image analysis result"
        # Verify that images were included in the messages
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) > 0
        user_message = messages[-1]
        assert "content" in user_message
        assert len(user_message["content"]) > 1  # Should have text and image

    @pytest.mark.asyncio
    async def test_generate_with_audio(self, provider, mock_openai_client):
        """Test generation with audio input (GPT-4o)."""
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Audio transcription result"

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Create a test request with audio
        request = TaskRequest(
            prompt="Transcribe this audio",
            task_type=TaskType.AUDIO_PROCESSING,
            audio="base64_encoded_audio_data",
        )

        # Test generation with GPT-4o (supports audio)
        response = await provider.generate(request, "gpt-4o")

        assert response.content == "Audio transcription result"
        # Verify that audio was included in the messages
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) > 0
        user_message = messages[-1]
        assert "content" in user_message
        assert len(user_message["content"]) > 1  # Should have text and audio

    @pytest.mark.asyncio
    async def test_generate_streaming(self, provider, mock_openai_client):
        """Test streaming generation."""
        # Mock the streaming response
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))]),
            Mock(choices=[Mock(delta=Mock(content=" world"))]),
            Mock(choices=[Mock(delta=Mock(content="!"))]),
        ]

        async def mock_stream():
            for chunk in mock_chunks:
                yield chunk

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_stream()
        )

        # Create a test request
        request = TaskRequest(
            prompt="Say hello world", task_type=TaskType.TEXT_GENERATION
        )

        # Test streaming generation
        chunks = []
        async for chunk in provider.generate_stream(request, "gpt-4"):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0] == "Hello"
        assert chunks[1] == " world"
        assert chunks[2] == "!"

    @pytest.mark.asyncio
    async def test_get_embeddings(self, provider, mock_openai_client):
        """Test embeddings generation."""
        # Mock the embeddings response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        # Test embeddings
        embeddings = await provider.get_embeddings("Test text", "gpt-4")

        assert isinstance(embeddings, list)
        assert len(embeddings) == 5
        assert all(isinstance(x, float) for x in embeddings)

    @pytest.mark.asyncio
    async def test_generate_api_error(self, provider, mock_openai_client):
        """Test handling of API errors."""
        # Mock an API error
        mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Create a test request
        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)

        # Test that the error is properly handled
        with pytest.raises(RuntimeError, match="OpenAI API call failed"):
            await provider.generate(request, "gpt-4")

    @pytest.mark.asyncio
    async def test_generate_empty_response(self, provider, mock_openai_client):
        """Test handling of empty API response."""
        # Mock an empty response
        mock_response = Mock()
        mock_response.choices = []

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Create a test request
        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)

        # Test that empty response is handled
        with pytest.raises(RuntimeError, match="OpenAI API call failed"):
            await provider.generate(request, "gpt-4")

    @pytest.mark.asyncio
    async def test_embeddings_api_error(self, provider, mock_openai_client):
        """Test handling of embeddings API errors."""
        # Mock an API error
        mock_openai_client.embeddings.create = AsyncMock(
            side_effect=Exception("Embeddings API Error")
        )

        # Test that the error is properly handled
        with pytest.raises(RuntimeError, match="OpenAI embeddings API call failed"):
            await provider.get_embeddings("Test text", "gpt-4")

    def test_model_suitability_for_tasks(self, provider):
        """Test model suitability for different task types."""
        # Test GPT-4 suitability
        gpt4_info = provider.models["gpt-4"]

        # Should be suitable for most tasks
        assert provider._is_model_suitable_for_task(gpt4_info, TaskType.TEXT_GENERATION)
        assert provider._is_model_suitable_for_task(gpt4_info, TaskType.CODE_GENERATION)
        assert provider._is_model_suitable_for_task(gpt4_info, TaskType.VISION_ANALYSIS)
        assert provider._is_model_suitable_for_task(gpt4_info, TaskType.MATH)
        assert provider._is_model_suitable_for_task(
            gpt4_info, TaskType.FUNCTION_CALLING
        )

        # Test GPT-3.5-turbo suitability (no vision)
        gpt35_info = provider.models["gpt-3.5-turbo"]

        assert provider._is_model_suitable_for_task(
            gpt35_info, TaskType.TEXT_GENERATION
        )
        assert provider._is_model_suitable_for_task(
            gpt35_info, TaskType.CODE_GENERATION
        )
        assert not provider._is_model_suitable_for_task(
            gpt35_info, TaskType.VISION_ANALYSIS
        )

    def test_performance_metrics_initialization(self, provider):
        """Test that performance metrics are properly initialized."""
        for model_name, model_info in provider.models.items():
            metrics = provider.get_performance_metrics(model_name)
            assert metrics is not None
            assert isinstance(metrics, PerformanceMetrics)

            # Check that key metrics are present
            assert metrics.mmlu_score is not None
            assert metrics.human_eval_score is not None
            assert metrics.latency_ms is not None
            assert metrics.cost_efficiency is not None
            assert metrics.reliability_score is not None

    def test_cost_efficiency_comparison(self, provider):
        """Test cost efficiency comparison between models."""
        # Get cost efficiency scores
        gpt4_efficiency = provider.models["gpt-4"].benchmark_scores["cost_efficiency"]
        gpt4o_efficiency = provider.models["gpt-4o"].benchmark_scores["cost_efficiency"]
        gpt4o_mini_efficiency = provider.models["gpt-4o-mini"].benchmark_scores[
            "cost_efficiency"
        ]

        # GPT-4o-mini should be most cost efficient
        assert gpt4o_mini_efficiency > gpt4o_efficiency
        assert gpt4o_mini_efficiency > gpt4_efficiency

    def test_latency_comparison(self, provider):
        """Test latency comparison between models."""
        # Get latency scores
        gpt4_latency = provider.models["gpt-4"].benchmark_scores["latency_ms"]
        gpt4o_latency = provider.models["gpt-4o"].benchmark_scores["latency_ms"]
        gpt4o_mini_latency = provider.models["gpt-4o-mini"].benchmark_scores[
            "latency_ms"
        ]

        # GPT-4o-mini should be fastest
        assert gpt4o_mini_latency < gpt4o_latency
        assert gpt4o_mini_latency < gpt4_latency

    def test_context_window_sizes(self, provider):
        """Test context window sizes for different models."""
        # All models should have reasonable context windows
        for model_name, model_info in provider.models.items():
            assert model_info.context_window > 0
            assert model_info.context_window >= model_info.max_tokens

    def test_max_tokens_limits(self, provider):
        """Test max tokens limits for different models."""
        # All models should have reasonable max token limits
        for model_name, model_info in provider.models.items():
            assert model_info.max_tokens > 0
            assert model_info.max_tokens <= model_info.context_window


class TestOpenAIProviderIntegration:
    """Integration tests for OpenAI provider with real API (if API key is available)."""

    @pytest.fixture
    def real_provider(self):
        """Create a real OpenAI provider instance if API key is available."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            pytest.skip("OpenAI API key not available for integration tests")
        return OpenAIProvider(api_key=api_key)

    @pytest.mark.asyncio
    async def test_real_api_call(self, real_provider):
        """Test real API call (requires valid API key)."""
        request = TaskRequest(
            prompt="Say hello in one word",
            task_type=TaskType.TEXT_GENERATION,
            max_tokens=10,
        )

        response = await real_provider.generate(request, "gpt-3.5-turbo")

        assert isinstance(response, TaskResponse)
        assert response.content is not None
        assert len(response.content) > 0
        assert response.model_used == "gpt-3.5-turbo"
        assert response.provider == "openai"

    @pytest.mark.asyncio
    async def test_real_embeddings_call(self, real_provider):
        """Test real embeddings API call (requires valid API key)."""
        embeddings = await real_provider.get_embeddings(
            "Test text for embeddings", "gpt-4"
        )

        assert isinstance(embeddings, list)
        assert len(embeddings) > 0
        assert all(isinstance(x, float) for x in embeddings)

    @pytest.mark.asyncio
    async def test_real_streaming_call(self, real_provider):
        """Test real streaming API call (requires valid API key)."""
        request = TaskRequest(
            prompt="Count from 1 to 5",
            task_type=TaskType.TEXT_GENERATION,
            max_tokens=50,
        )

        chunks = []
        async for chunk in real_provider.generate_stream(request, "gpt-3.5-turbo"):
            chunks.append(chunk)

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
