"""
Example tests demonstrating OpenAI provider usage.

This module shows how to use the OpenAI provider for various tasks
and serves as documentation for developers.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from llm_dispatcher.providers.openai_provider import OpenAIProvider
from llm_dispatcher.core.base import TaskRequest, TaskType, Capability


class TestOpenAIExamples:
    """Example tests showing OpenAI provider usage patterns."""

    @pytest.fixture
    def provider(self):
        """Create a test OpenAI provider instance."""
        api_key = os.getenv("OPENAI_API_KEY", "test_api_key")
        return OpenAIProvider(api_key=api_key)

    def test_basic_text_generation_example(self, provider):
        """Example: Basic text generation."""
        # Create a text generation request
        request = TaskRequest(
            prompt="Write a haiku about artificial intelligence",
            task_type=TaskType.TEXT_GENERATION,
            temperature=0.8,
            max_tokens=100,
        )

        # Get the best model for text generation
        best_model = provider.get_best_model_for_task(TaskType.TEXT_GENERATION)
        assert best_model is not None

        # Check that the model supports text generation
        model_info = provider.get_model_info(best_model)
        assert Capability.TEXT in model_info.capabilities

    def test_code_generation_example(self, provider):
        """Example: Code generation with performance comparison."""
        # Create a code generation request
        request = TaskRequest(
            prompt="Write a Python function to calculate the factorial of a number",
            task_type=TaskType.CODE_GENERATION,
            temperature=0.3,
            max_tokens=300,
        )

        # Get all models suitable for code generation
        code_models = provider.get_models_for_task(TaskType.CODE_GENERATION)
        assert len(code_models) > 0

        # Compare performance scores for code generation
        performance_scores = {}
        for model in code_models:
            score = provider.get_performance_score(model, TaskType.CODE_GENERATION)
            performance_scores[model] = score

        # Find the best performing model
        best_model = max(performance_scores, key=performance_scores.get)
        assert best_model is not None
        assert performance_scores[best_model] > 0

    def test_vision_analysis_example(self, provider):
        """Example: Vision analysis with model selection."""
        # Create a vision analysis request
        request = TaskRequest(
            prompt="Describe what you see in this image",
            task_type=TaskType.VISION_ANALYSIS,
            images=["base64_encoded_image_data"],
            temperature=0.2,
        )

        # Get models that support vision
        vision_models = provider.get_models_for_task(TaskType.VISION_ANALYSIS)
        assert len(vision_models) > 0

        # Verify all models have vision capability
        for model in vision_models:
            model_info = provider.get_model_info(model)
            assert Capability.VISION in model_info.capabilities

    def test_math_problem_solving_example(self, provider):
        """Example: Math problem solving with performance ranking."""
        # Create a math request
        request = TaskRequest(
            prompt="Solve the quadratic equation: x² + 5x + 6 = 0",
            task_type=TaskType.MATH,
            temperature=0.1,
            max_tokens=200,
        )

        # Get performance ranking for math tasks
        math_rankings = provider.get_performance_ranking(TaskType.MATH)
        assert len(math_rankings) > 0

        # Verify rankings are sorted (best first)
        for i in range(len(math_rankings) - 1):
            assert math_rankings[i][1] >= math_rankings[i + 1][1]

    def test_cost_optimization_example(self, provider):
        """Example: Cost optimization for budget-conscious usage."""
        # Create a request
        request = TaskRequest(
            prompt="Summarize the key points of machine learning",
            task_type=TaskType.SUMMARIZATION,
            max_tokens=200,
        )

        # Estimate costs for different models
        estimated_input_tokens = 100
        estimated_output_tokens = 200

        cost_estimates = provider.get_cost_estimate(
            TaskType.SUMMARIZATION, estimated_input_tokens, estimated_output_tokens
        )

        assert len(cost_estimates) > 0

        # Find the most cost-effective model
        cheapest_model = min(cost_estimates, key=cost_estimates.get)
        assert cheapest_model is not None
        assert cost_estimates[cheapest_model] >= 0

    def test_structured_output_example(self, provider):
        """Example: Structured output generation."""
        # Create a request for structured output
        request = TaskRequest(
            prompt="Generate a JSON object with information about Python programming",
            task_type=TaskType.TEXT_GENERATION,
            structured_output={"type": "json_object"},
            temperature=0.5,
        )

        # Get models that support structured output
        structured_models = []
        for model_name, model_info in provider.models.items():
            if Capability.STRUCTURED_OUTPUT in model_info.capabilities:
                structured_models.append(model_name)

        assert len(structured_models) > 0

    def test_function_calling_example(self, provider):
        """Example: Function calling capabilities."""
        # Define a function schema
        functions = [
            {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                },
            }
        ]

        # Create a function calling request
        request = TaskRequest(
            prompt="What's the weather like in New York?",
            task_type=TaskType.FUNCTION_CALLING,
            functions=functions,
            temperature=0.3,
        )

        # Get models that support function calling
        function_models = []
        for model_name, model_info in provider.models.items():
            if Capability.FUNCTION_CALLING in model_info.capabilities:
                function_models.append(model_name)

        assert len(function_models) > 0

    def test_audio_processing_example(self, provider):
        """Example: Audio processing with GPT-4o."""
        # Create an audio processing request
        request = TaskRequest(
            prompt="Transcribe this audio file",
            task_type=TaskType.AUDIO_PROCESSING,
            audio="base64_encoded_audio_data",
            temperature=0.1,
        )

        # Get models that support audio processing
        audio_models = []
        for model_name, model_info in provider.models.items():
            if Capability.AUDIO in model_info.capabilities:
                audio_models.append(model_name)

        # GPT-4o should support audio
        assert "gpt-4o" in audio_models

    def test_performance_comparison_example(self, provider):
        """Example: Comparing models across different metrics."""
        # Compare models for different tasks
        tasks = [
            TaskType.TEXT_GENERATION,
            TaskType.CODE_GENERATION,
            TaskType.MATH,
            TaskType.VISION_ANALYSIS,
        ]

        comparison_results = {}

        for task in tasks:
            rankings = provider.get_performance_ranking(task)
            if rankings:
                best_model, best_score = rankings[0]
                comparison_results[task] = {
                    "best_model": best_model,
                    "best_score": best_score,
                }

        assert len(comparison_results) > 0

        # Verify that we have results for each task
        for task in tasks:
            if task in comparison_results:
                assert comparison_results[task]["best_score"] > 0

    def test_model_capability_matrix_example(self, provider):
        """Example: Creating a capability matrix for all models."""
        # Create a capability matrix
        capabilities = list(Capability)
        models = list(provider.models.keys())

        capability_matrix = {}

        for model in models:
            model_info = provider.get_model_info(model)
            capability_matrix[model] = {
                capability: capability in model_info.capabilities
                for capability in capabilities
            }

        assert len(capability_matrix) > 0

        # Verify that each model has at least text capability
        for model, capabilities_dict in capability_matrix.items():
            assert capabilities_dict[Capability.TEXT] is True

    def test_benchmark_scores_example(self, provider):
        """Example: Accessing and comparing benchmark scores."""
        # Get benchmark scores for different models
        benchmark_comparison = {}

        for model_name, model_info in provider.models.items():
            scores = model_info.benchmark_scores
            benchmark_comparison[model_name] = {
                "mmlu": scores.get("mmlu", 0),
                "human_eval": scores.get("human_eval", 0),
                "aime": scores.get("aime", 0),
                "cost_efficiency": scores.get("cost_efficiency", 0),
                "latency_ms": scores.get("latency_ms", 0),
            }

        assert len(benchmark_comparison) > 0

        # Find the model with highest MMLU score
        best_mmlu_model = max(benchmark_comparison.items(), key=lambda x: x[1]["mmlu"])
        assert best_mmlu_model[1]["mmlu"] > 0

    def test_token_estimation_example(self, provider):
        """Example: Token estimation for cost planning."""
        # Test different types of text
        test_texts = [
            "Short text",
            "This is a longer text that should have more tokens and help us understand how token estimation works.",
            "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "Write a comprehensive analysis of machine learning algorithms including supervised learning, unsupervised learning, and reinforcement learning approaches.",
        ]

        token_estimates = {}
        for text in test_texts:
            tokens = provider.estimate_tokens(text)
            token_estimates[text[:20] + "..."] = tokens

        assert len(token_estimates) > 0

        # Verify that longer texts have more tokens
        assert (
            token_estimates["Short text"] < token_estimates["Write a comprehensive..."]
        )

    @pytest.mark.asyncio
    async def test_async_usage_example(self, provider):
        """Example: Async usage patterns."""
        # This example shows how to use the provider asynchronously
        # (Note: This uses mocked responses for testing)

        with patch.object(provider, "_make_api_call") as mock_api_call:
            mock_api_call.return_value = "This is a test response"

            request = TaskRequest(
                prompt="Test async prompt", task_type=TaskType.TEXT_GENERATION
            )

            # Test async generation
            response = await provider.generate(request, "gpt-4")
            assert response.content == "This is a test response"
            assert response.model_used == "gpt-4"
            assert response.provider == "openai"

    def test_error_handling_example(self, provider):
        """Example: Error handling patterns."""
        # Test with invalid model
        invalid_model = "non-existent-model"
        model_info = provider.get_model_info(invalid_model)
        assert model_info is None

        # Test with invalid task type
        try:
            # This should not raise an exception
            models = provider.get_models_for_task("invalid_task_type")
            assert isinstance(models, list)
        except Exception:
            # If it does raise an exception, that's also acceptable
            pass

    def test_configuration_example(self, provider):
        """Example: Configuration and customization."""
        # Test different temperature settings
        temperatures = [0.1, 0.5, 0.8, 1.0]

        for temp in temperatures:
            request = TaskRequest(
                prompt="Generate creative text",
                task_type=TaskType.TEXT_GENERATION,
                temperature=temp,
            )
            assert request.temperature == temp

        # Test different max_tokens settings
        max_tokens_values = [100, 500, 1000, 2000]

        for max_tokens in max_tokens_values:
            request = TaskRequest(
                prompt="Generate text",
                task_type=TaskType.TEXT_GENERATION,
                max_tokens=max_tokens,
            )
            assert request.max_tokens == max_tokens


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
