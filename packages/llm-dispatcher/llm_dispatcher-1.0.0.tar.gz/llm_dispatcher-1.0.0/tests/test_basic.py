"""
Basic tests for LLM-Dispatcher package.

This module contains basic tests to verify the core functionality
of the LLM-Dispatcher package.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from llm_dispatcher.core.base import TaskType, Capability, TaskRequest
from llm_dispatcher.utils.benchmark_manager import BenchmarkManager
from llm_dispatcher.utils.task_classifier import TaskClassifier
from llm_dispatcher.config.settings import SwitchConfig


class TestBenchmarkManager:
    """Test the benchmark manager."""

    def test_benchmark_manager_initialization(self):
        """Test benchmark manager initialization."""
        manager = BenchmarkManager()
        assert manager is not None
        assert len(manager.benchmark_data) > 0

    def test_get_benchmark_scores(self):
        """Test getting benchmark scores for a model."""
        manager = BenchmarkManager()
        scores = manager.get_benchmark_scores("gpt-4")
        assert scores is not None
        assert "mmlu" in scores
        assert "human_eval" in scores

    def test_get_performance_metrics(self):
        """Test getting performance metrics."""
        manager = BenchmarkManager()
        metrics = manager.get_performance_metrics("gpt-4")
        assert metrics is not None
        assert metrics.mmlu_score is not None
        assert metrics.human_eval_score is not None

    def test_get_task_performance_ranking(self):
        """Test getting task performance rankings."""
        manager = BenchmarkManager()
        rankings = manager.get_task_performance_ranking(TaskType.CODE_GENERATION)
        assert len(rankings) > 0
        assert all(isinstance(score, float) for _, score in rankings)


class TestTaskClassifier:
    """Test the task classifier."""

    def test_task_classifier_initialization(self):
        """Test task classifier initialization."""
        classifier = TaskClassifier()
        assert classifier is not None
        assert len(classifier.keywords) > 0

    def test_classify_text_generation(self):
        """Test classification of text generation tasks."""
        classifier = TaskClassifier()
        task_type, confidence = classifier.classify("Write a story about a robot")
        assert task_type == TaskType.TEXT_GENERATION
        assert confidence > 0

    def test_classify_code_generation(self):
        """Test classification of code generation tasks."""
        classifier = TaskClassifier()
        task_type, confidence = classifier.classify(
            "Write a Python function to sort a list"
        )
        assert task_type == TaskType.CODE_GENERATION
        assert confidence > 0

    def test_classify_question_answering(self):
        """Test classification of question answering tasks."""
        classifier = TaskClassifier()
        task_type, confidence = classifier.classify("What is the capital of France?")
        assert task_type == TaskType.QUESTION_ANSWERING
        assert confidence > 0

    def test_classify_math(self):
        """Test classification of math tasks."""
        classifier = TaskClassifier()
        task_type, confidence = classifier.classify("Solve the equation 2x + 5 = 15")
        assert task_type == TaskType.MATH
        assert confidence > 0

    def test_get_top_candidates(self):
        """Test getting top task candidates."""
        classifier = TaskClassifier()
        candidates = classifier.get_top_candidates(
            "Write a function to calculate fibonacci numbers", 3
        )
        assert len(candidates) == 3
        assert all(isinstance(score, float) for _, score in candidates)


class TestSwitchConfig:
    """Test the switch configuration."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = SwitchConfig()
        assert config is not None
        assert config.switching_rules is not None

    def test_config_validation(self):
        """Test configuration validation."""
        config = SwitchConfig()
        errors = config.validate_config()
        # Should have no errors for default config
        assert len(errors) == 0

    def test_provider_config(self):
        """Test provider configuration."""
        from llm_dispatcher.config.settings import ProviderConfig

        provider_config = ProviderConfig(
            name="test_provider", api_key="test_key", models=["model1", "model2"]
        )
        assert provider_config.name == "test_provider"
        assert provider_config.api_key == "test_key"
        assert len(provider_config.models) == 2


class TestTaskRequest:
    """Test the task request structure."""

    def test_task_request_creation(self):
        """Test creating a task request."""
        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)
        assert request.prompt == "Test prompt"
        assert request.task_type == TaskType.TEXT_GENERATION
        assert request.temperature == 0.7  # Default value

    def test_task_request_with_metadata(self):
        """Test creating a task request with metadata."""
        metadata = {"source": "test", "priority": "high"}
        request = TaskRequest(
            prompt="Test prompt", task_type=TaskType.TEXT_GENERATION, metadata=metadata
        )
        assert request.metadata == metadata


class TestCapabilities:
    """Test capability definitions."""

    def test_capability_enum(self):
        """Test capability enum values."""
        assert Capability.TEXT in Capability
        assert Capability.VISION in Capability
        assert Capability.AUDIO in Capability
        assert Capability.CODE in Capability

    def test_task_type_enum(self):
        """Test task type enum values."""
        assert TaskType.TEXT_GENERATION in TaskType
        assert TaskType.CODE_GENERATION in TaskType
        assert TaskType.VISION_ANALYSIS in TaskType
        assert TaskType.MATH in TaskType


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality."""

    async def test_async_task_creation(self):
        """Test async task creation."""
        request = TaskRequest(
            prompt="Async test prompt", task_type=TaskType.TEXT_GENERATION
        )
        assert request.prompt == "Async test prompt"
        assert request.task_type == TaskType.TEXT_GENERATION


class TestOpenAIProviderBasics:
    """Test basic OpenAI provider functionality."""

    def test_openai_provider_import(self):
        """Test that OpenAI provider can be imported."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        assert OpenAIProvider is not None

    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")
        assert provider is not None
        assert provider.provider_name == "openai"
        assert len(provider.models) > 0

    def test_openai_models_available(self):
        """Test that OpenAI models are available."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")
        expected_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ]

        for model in expected_models:
            assert model in provider.models

    def test_openai_model_capabilities(self):
        """Test OpenAI model capabilities."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")

        # GPT-4 should have vision capability
        gpt4_info = provider.models["gpt-4"]
        assert Capability.VISION in gpt4_info.capabilities

        # GPT-4o should have audio capability
        gpt4o_info = provider.models["gpt-4o"]
        assert Capability.AUDIO in gpt4o_info.capabilities

        # GPT-3.5-turbo should not have vision
        gpt35_info = provider.models["gpt-3.5-turbo"]
        assert Capability.VISION not in gpt35_info.capabilities

    def test_openai_benchmark_scores(self):
        """Test that OpenAI models have benchmark scores."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")

        for model_name, model_info in provider.models.items():
            scores = model_info.benchmark_scores
            assert "mmlu" in scores
            assert "human_eval" in scores
            assert scores["mmlu"] > 0
            assert scores["human_eval"] > 0

    def test_openai_cost_estimation(self):
        """Test OpenAI cost estimation."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")

        # Test cost estimation
        cost = provider.estimate_cost("gpt-4", 1000, 500)
        assert cost > 0

        # Test that GPT-4 is more expensive than GPT-3.5
        gpt4_cost = provider.estimate_cost("gpt-4", 1000, 500)
        gpt35_cost = provider.estimate_cost("gpt-3.5-turbo", 1000, 500)
        assert gpt4_cost > gpt35_cost

    def test_openai_performance_scores(self):
        """Test OpenAI performance score calculation."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")

        # Test code generation performance
        gpt4_code_score = provider.get_performance_score(
            "gpt-4", TaskType.CODE_GENERATION
        )
        assert gpt4_code_score > 0
        assert gpt4_code_score <= 1.0

        # Test math performance
        gpt4_math_score = provider.get_performance_score("gpt-4", TaskType.MATH)
        assert gpt4_math_score > 0
        assert gpt4_math_score <= 1.0

    def test_openai_model_selection(self):
        """Test OpenAI model selection for tasks."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")

        # Test code generation models
        code_models = provider.get_models_for_task(TaskType.CODE_GENERATION)
        assert len(code_models) > 0
        assert all(model in provider.models for model in code_models)

        # Test vision models
        vision_models = provider.get_models_for_task(TaskType.VISION_ANALYSIS)
        assert len(vision_models) > 0
        # Should only include models with vision capability
        for model in vision_models:
            assert Capability.VISION in provider.models[model].capabilities

    def test_openai_best_model_selection(self):
        """Test OpenAI best model selection."""
        from llm_dispatcher.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key")

        # Test best model for code generation
        best_code_model = provider.get_best_model_for_task(TaskType.CODE_GENERATION)
        assert best_code_model is not None
        assert best_code_model in provider.models

        # Test best model for vision
        best_vision_model = provider.get_best_model_for_task(TaskType.VISION_ANALYSIS)
        assert best_vision_model is not None
        assert Capability.VISION in provider.models[best_vision_model].capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
