"""
Integration tests for LLM-Dispatcher.

This module contains comprehensive integration tests that verify
end-to-end functionality across multiple components.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from datetime import datetime

from llm_dispatcher import LLMSwitch, llm_dispatcher
from llm_dispatcher.core import TaskType, Capability, TaskRequest, TaskResponse
from llm_dispatcher.config import (
    SwitchConfig,
    OptimizationStrategy,
    FallbackStrategy,
    SwitchingRules,
)
from llm_dispatcher.providers import BaseProvider
from llm_dispatcher.utils import BenchmarkManager, CostCalculator, PerformanceMonitor
from llm_dispatcher.multimodal import MultimodalAnalyzer, MediaValidator


class MockProvider(BaseProvider):
    """Mock provider for testing."""

    def __init__(self, name: str, models: list = None):
        self.name = name
        self.provider_name = name
        # Convert list of model names to dictionary of ModelInfo objects
        model_names = models or []
        self.models = {}
        for model_name in model_names:
            from llm_dispatcher.core.base import ModelInfo, Capability

            self.models[model_name] = ModelInfo(
                name=model_name,
                provider=name,
                capabilities=[Capability.TEXT, Capability.CODE],
                max_tokens=4096,
                context_window=8192,
                cost_per_1k_tokens={"input": 0.01, "output": 0.02},
            )
        self.performance_metrics = {}
        self.health_status = {"status": "healthy", "last_check": datetime.now()}

        # Initialize statistics tracking
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0.0
        self.total_latency = 0.0  # Also need this for base provider
        self.total_cost = 0.0

    async def _make_api_call(self, request: TaskRequest, model: str) -> str:
        """Mock API call."""
        return f"Mock response from {self.name}"

    async def _make_streaming_api_call(self, request: TaskRequest, model: str):
        """Mock streaming API call."""
        for i in range(3):
            yield f"chunk_{i}_from_{self.name}"

    async def _make_embeddings_call(self, text: str) -> list:
        """Mock embeddings call."""
        return [0.1, 0.2, 0.3] * 10  # 30-dimensional embedding

    def _initialize_models(self):
        """Initialize mock models."""
        pass

    def _initialize_performance_metrics(self):
        """Initialize mock performance metrics."""
        pass


class TestLLMSwitchIntegration:
    """Integration tests for LLMSwitch."""

    @pytest.fixture
    def mock_providers(self):
        """Create mock providers for testing."""
        provider1 = MockProvider("provider1", ["model1", "model2"])
        provider2 = MockProvider("provider2", ["model3", "model4"])
        return {"provider1": provider1, "provider2": provider2}

    @pytest.fixture
    def switch_config(self):
        """Create switch configuration."""
        return SwitchConfig(
            switching_rules=SwitchingRules(
                optimization_strategy=OptimizationStrategy.BALANCED,
                fallback_strategy=FallbackStrategy.PERFORMANCE_PRIORITY,
                max_cost_per_request=1.0,
                max_latency_ms=5000,
                enable_caching=True,
            )
        )

    @pytest.fixture
    def llm_switch(self, mock_providers, switch_config):
        """Create LLMSwitch instance for testing."""
        return LLMSwitch(providers=mock_providers, config=switch_config)

    @pytest.mark.asyncio
    async def test_end_to_end_request_processing(self, llm_switch):
        """Test complete request processing pipeline."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        response = await llm_switch.execute_with_fallback(request)

        assert isinstance(response, TaskResponse)
        assert response.content is not None
        assert response.provider in ["provider1", "provider2"]
        assert response.tokens_used > 0
        assert response.cost > 0

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, llm_switch):
        """Test fallback mechanism when primary provider fails."""
        # Mock first provider to fail
        llm_switch.providers["provider1"]._make_api_call = AsyncMock(
            side_effect=Exception("Provider failed")
        )

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        response = await llm_switch.execute_with_fallback(request)

        # Should fallback to second provider
        assert response.provider == "provider2"
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_streaming_response(self, llm_switch):
        """Test streaming response handling."""
        request = TaskRequest(
            prompt="Test streaming prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        chunks = []
        async for chunk in llm_switch.execute_stream(request):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    @pytest.mark.asyncio
    async def test_model_selection_logic(self, llm_switch):
        """Test model selection based on task type."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.CODE_GENERATION,
        )

        decision = await llm_switch.select_llm(request)

        assert decision is not None
        assert decision.provider in ["provider1", "provider2"]
        assert decision.model in ["model1", "model2", "model3", "model4"]

    def test_cost_constraints(self, llm_switch):
        """Test cost constraint enforcement."""
        # Set very low cost constraint
        llm_switch.config.switching_rules.max_cost_per_request = 0.0001

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        decision = llm_switch.select_llm(request)

        # Should still select a model (fallback to cheapest)
        assert decision is not None

    def test_latency_constraints(self, llm_switch):
        """Test latency constraint enforcement."""
        # Set very low latency constraint
        llm_switch.config.switching_rules.max_latency_ms = 100

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        decision = llm_switch.select_llm(request)

        # Should still select a model
        assert decision is not None

    def test_system_status(self, llm_switch):
        """Test system status reporting."""
        status = llm_switch.get_system_status()

        # Check that we have the expected keys in the status
        assert "total_providers" in status
        assert "total_models" in status
        assert "provider_health" in status
        assert "performance_summary" in status

        # Check that we have 2 providers
        assert status["total_providers"] == 2
        assert len(status["provider_health"]) == 2

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, llm_switch):
        """Test handling of concurrent requests."""
        request = TaskRequest(
            prompt="Concurrent test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Execute multiple requests concurrently
        tasks = [llm_switch.execute_with_fallback(request) for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        assert len(responses) == 5
        assert all(isinstance(response, TaskResponse) for response in responses)
        assert all(response.content is not None for response in responses)


class TestDecoratorIntegration:
    """Integration tests for decorator functionality."""

    @pytest.fixture
    def mock_switch(self):
        """Create mock LLMSwitch for decorator testing."""
        switch = Mock()
        switch.execute_with_fallback = AsyncMock(
            return_value=TaskResponse(
                content="Decorator test response",
                model_used="test-model",
                provider="test-provider",
                tokens_used=50,
                cost=0.0005,
                latency_ms=300,
                finish_reason="stop",
            )
        )
        return switch

    @pytest.mark.asyncio
    async def test_basic_decorator_functionality(self, mock_switch):
        """Test basic decorator functionality."""
        with patch(
            "llm_dispatcher.decorators.switch_decorator._global_switch", mock_switch
        ):

            @llm_dispatcher()
            async def test_function(prompt: str) -> str:
                return prompt

            result = await test_function("Test prompt")

            assert result == "Decorator test response"
            mock_switch.execute_with_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_decorator_with_task_type(self, mock_switch):
        """Test decorator with specific task type."""
        with patch(
            "llm_dispatcher.decorators.switch_decorator._global_switch", mock_switch
        ):

            @llm_dispatcher(task_type=TaskType.CODE_GENERATION)
            async def code_function(code: str) -> str:
                return code

            result = await code_function("print('hello')")

            assert result == "Decorator test response"
            call_args = mock_switch.execute_with_fallback.call_args[0][0]
            assert call_args.task_type == TaskType.CODE_GENERATION

    def test_sync_function_decorator(self, mock_switch):
        """Test decorator with sync function."""
        with patch(
            "llm_dispatcher.decorators.switch_decorator._global_switch", mock_switch
        ):

            @llm_dispatcher()
            def sync_function(prompt: str) -> str:
                return prompt

            # Mock the async execution for sync functions
            mock_switch.execute_with_fallback = Mock(
                return_value=TaskResponse(
                    content="Sync test response",
                    model_used="test-model",
                    provider="test-provider",
                    tokens_used=50,
                    cost=0.0005,
                    latency_ms=300,
                    finish_reason="stop",
                )
            )

            result = sync_function("Test sync prompt")

            assert result == "Sync test response"
            mock_switch.execute_with_fallback.assert_called_once()


class TestMultimodalIntegration:
    """Integration tests for multimodal functionality."""

    @pytest.fixture
    def sample_image_data(self):
        """Create sample image data for testing."""
        from PIL import Image
        import io

        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    def test_multimodal_analysis_pipeline(self, sample_image_data):
        """Test complete multimodal analysis pipeline."""
        analyzer = MultimodalAnalyzer()
        validator = MediaValidator()

        # Test validation
        validation_result = validator.validate_media(sample_image_data)
        assert validation_result.is_valid

        # Test analysis
        media_data = {"test_image": sample_image_data}
        analysis_result = analyzer.analyze_multimodal_content(media_data)

        assert analysis_result.media_analysis["test_image"]["valid"] is True
        assert analysis_result.content_analysis is not None
        assert analysis_result.task_recommendation is not None

    def test_multimodal_with_llm_switch(self, sample_image_data):
        """Test multimodal integration with LLMSwitch."""
        # This would require actual LLM integration
        # For now, just test that the components work together
        analyzer = MultimodalAnalyzer()
        validator = MediaValidator()

        # Validate media
        validation_result = validator.validate_media(sample_image_data)
        assert validation_result.is_valid

        # Analyze for task recommendation
        media_data = {"image": sample_image_data}
        analysis_result = analyzer.analyze_multimodal_content(
            media_data, task_description="Analyze this image"
        )

        recommendation = analysis_result.task_recommendation
        assert recommendation.recommended_providers is not None
        assert recommendation.optimal_model is not None
        assert recommendation.estimated_cost > 0


class TestPerformanceIntegration:
    """Integration tests for performance monitoring."""

    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor for testing."""
        return PerformanceMonitor()

    def test_performance_metrics_collection(self, performance_monitor):
        """Test performance metrics collection and aggregation."""
        # Simulate some performance data
        for i in range(10):
            performance_monitor.record_metric(
                "latency_ms", 100 + i * 10, {"provider": "test"}
            )

        # Get aggregated metrics
        stats = performance_monitor.get_metric_stats("latency_ms")

        assert stats.count == 10
        assert stats.min <= stats.max
        assert stats.mean > 0

    def test_benchmark_manager_integration(self):
        """Test benchmark manager integration."""
        benchmark_manager = BenchmarkManager()

        # Test getting benchmark scores
        scores = benchmark_manager.get_benchmark_scores("gpt-4")
        assert isinstance(scores, dict)

        # Test performance ranking
        ranking = benchmark_manager.get_task_performance_ranking("text_generation")
        assert isinstance(ranking, list)
        assert len(ranking) > 0

    def test_cost_calculator_integration(self):
        """Test cost calculator integration."""
        cost_calculator = CostCalculator()

        # Test cost tracking
        cost_calculator.track_cost("provider1", "model1", 100, 0.001)

        # Test cost efficiency ranking
        ranking = cost_calculator.get_cost_efficiency_ranking()
        assert isinstance(ranking, list)


class TestCachingIntegration:
    """Integration tests for caching functionality."""

    def test_cache_manager_integration(self):
        """Test cache manager integration."""
        from llm_dispatcher.caching import CacheManager

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_manager = CacheManager(
                cache_dir=temp_dir, max_size_mb=10, cleanup_interval=60
            )

            try:
                cache_manager.start()

                # Test cache operations
                cache_manager.put("test_key", "test_value", tags=["test"])
                cached_value = cache_manager.get("test_key")

                assert cached_value == "test_value"

                # Test cache stats
                stats = cache_manager.get_cache_stats()
                assert stats["hits"] >= 0
                assert stats["misses"] >= 0

            finally:
                cache_manager.stop()

    def test_semantic_cache_integration(self):
        """Test semantic cache integration."""
        from llm_dispatcher.caching import SemanticCache

        with tempfile.TemporaryDirectory() as temp_dir:
            semantic_cache = SemanticCache(cache_dir=temp_dir, similarity_threshold=0.8)

            # Test semantic caching
            semantic_cache.add_to_semantic_cache(
                "What is the weather?", "It's sunny today", {}
            )

            # Test similarity search
            similar_response = semantic_cache.find_best_similar_response(
                "How's the weather?"
            )

            assert similar_response is not None
            assert similar_response["response"] == "It's sunny today"


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    @pytest.mark.asyncio
    async def test_provider_failure_handling(self):
        """Test handling of provider failures."""
        # Create a provider that always fails
        failing_provider = MockProvider("failing_provider")
        failing_provider._make_api_call = AsyncMock(
            side_effect=Exception("Provider failed")
        )

        working_provider = MockProvider("working_provider")

        switch = LLMSwitch(providers=[failing_provider, working_provider])

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Should fallback to working provider
        response = await switch.execute_with_fallback(request)

        assert response.provider == "working_provider"
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test handling when all providers fail."""
        # Create providers that all fail
        failing_provider1 = MockProvider("failing_provider1")
        failing_provider1._make_api_call = AsyncMock(
            side_effect=Exception("Provider 1 failed")
        )

        failing_provider2 = MockProvider("failing_provider2")
        failing_provider2._make_api_call = AsyncMock(
            side_effect=Exception("Provider 2 failed")
        )

        switch = LLMSwitch(providers=[failing_provider1, failing_provider2])

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Should raise exception when all providers fail
        with pytest.raises(Exception):
            await switch.execute_with_fallback(request)

    def test_invalid_configuration_handling(self):
        """Test handling of invalid configurations."""
        # Test with invalid optimization strategy
        with pytest.raises(ValueError):
            SwitchConfig(optimization_strategy="invalid_strategy")

        # Test with negative cost constraint
        with pytest.raises(ValueError):
            SwitchConfig(max_cost_per_request=-1.0)


class TestDataPersistence:
    """Integration tests for data persistence."""

    def test_config_persistence(self):
        """Test configuration persistence."""
        config = SwitchConfig(
            optimization_strategy=OptimizationStrategy.COST_OPTIMIZED,
            fallback_strategy=FallbackStrategy.COST_BASED,
            max_cost_per_request=0.5,
            enable_caching=True,
        )

        # Test configuration validation
        assert config.optimization_strategy == OptimizationStrategy.COST_OPTIMIZED
        assert config.max_cost_per_request == 0.5
        assert config.enable_caching is True

    def test_benchmark_data_persistence(self):
        """Test benchmark data persistence."""
        benchmark_manager = BenchmarkManager()

        # Test data export/import
        export_data = benchmark_manager.export_benchmark_data()
        assert isinstance(export_data, dict)

        # Test updating benchmark data
        benchmark_manager.update_benchmark_data(
            "test_model", {"text_generation": 0.85, "code_generation": 0.90}
        )

        scores = benchmark_manager.get_benchmark_scores("test_model")
        assert scores["text_generation"] == 0.85
        assert scores["code_generation"] == 0.90
