"""
Performance tests for LLM-Dispatcher.

This module contains performance and load tests to ensure
the system can handle production workloads efficiently.
"""

import pytest
import asyncio
import time
import statistics
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
import psutil
import os

from llm_dispatcher import LLMSwitch
from llm_dispatcher.core import (
    TaskType,
    TaskRequest,
    TaskResponse,
    ModelInfo,
    Capability,
)
from llm_dispatcher.config import SwitchConfig, OptimizationStrategy
from llm_dispatcher.utils import PerformanceMonitor, BenchmarkManager
from llm_dispatcher.providers import BaseProvider


class PerformanceTestProvider(BaseProvider):
    """Provider for performance testing."""

    def __init__(self, name: str, latency_ms: int = 100, success_rate: float = 1.0):
        super().__init__(api_key="test_key", provider_name=name)
        self.name = name
        self.provider_name = name
        self.latency_ms = latency_ms
        self.success_rate = success_rate
        self.models = {
            f"{name}-model": ModelInfo(
                name=f"{name}-model",
                provider=name,
                capabilities=[Capability.TEXT],
                max_tokens=4000,
                context_window=8000,
                benchmark_scores={"mmlu": 0.8, "human_eval": 0.7},
            )
        }
        self.performance_metrics = {}
        self.health_status = {"status": "healthy", "last_check": datetime.now()}
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0.0

    def _initialize_models(self) -> None:
        """Initialize models - already done in __init__."""
        pass

    async def _make_api_call(self, request: TaskRequest, model: str) -> str:
        """Simulate API call with controlled latency."""
        # Simulate network latency
        await asyncio.sleep(self.latency_ms / 1000.0)

        # Simulate occasional failures
        if self.success_rate < 1.0:
            import random

            if random.random() > self.success_rate:
                raise Exception(f"Simulated failure in {self.name}")

        return f"Response from {self.name}"

    async def _make_streaming_api_call(self, request: TaskRequest):
        """Simulate streaming API call."""
        chunk_count = 5
        chunk_delay = self.latency_ms / chunk_count / 1000.0

        for i in range(chunk_count):
            await asyncio.sleep(chunk_delay)
            yield f"chunk_{i}_from_{self.name}"

    async def _make_embeddings_call(self, text: str) -> list:
        """Simulate embeddings call."""
        await asyncio.sleep(self.latency_ms / 1000.0)
        return [0.1] * 384  # 384-dimensional embedding

    def _initialize_models(self):
        """Initialize models."""
        pass

    def _initialize_performance_metrics(self):
        """Initialize performance metrics."""
        pass


class TestLatencyPerformance:
    """Test latency performance under various conditions."""

    @pytest.fixture
    def fast_provider(self):
        """Create fast provider (10ms latency)."""
        return PerformanceTestProvider("fast", latency_ms=10)

    @pytest.fixture
    def slow_provider(self):
        """Create slow provider (500ms latency)."""
        return PerformanceTestProvider("slow", latency_ms=500)

    @pytest.fixture
    def mixed_providers(self, fast_provider, slow_provider):
        """Create mix of fast and slow providers."""
        return {"fast_provider": fast_provider, "slow_provider": slow_provider}

    @pytest.mark.asyncio
    async def test_single_request_latency(self, fast_provider):
        """Test latency of single request."""
        switch = LLMSwitch(providers={"fast_provider": fast_provider})

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        start_time = time.time()
        response = await switch.execute_with_fallback(request)
        end_time = time.time()

        actual_latency = (end_time - start_time) * 1000  # Convert to ms

        # Should be close to provider latency (within 50ms tolerance)
        assert abs(actual_latency - fast_provider.latency_ms) < 50
        # Allow for some execution overhead
        assert abs(response.latency_ms - fast_provider.latency_ms) < 5

    @pytest.mark.asyncio
    async def test_concurrent_requests_latency(self, mixed_providers):
        """Test latency under concurrent load."""
        switch = LLMSwitch(providers=mixed_providers)

        request = TaskRequest(
            prompt="Concurrent test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Execute 10 concurrent requests
        start_time = time.time()
        tasks = [switch.execute_with_fallback(request) for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = (end_time - start_time) * 1000

        # Concurrent execution should be faster than sequential
        sequential_time = sum(p.latency_ms for p in mixed_providers.values()) * 10
        assert total_time < sequential_time

        # All requests should complete
        assert len(responses) == 10
        assert all(isinstance(r, TaskResponse) for r in responses)

    @pytest.mark.asyncio
    async def test_streaming_latency(self, fast_provider):
        """Test streaming response latency."""
        switch = LLMSwitch(providers={"fast_provider": fast_provider})

        request = TaskRequest(
            prompt="Streaming test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        start_time = time.time()
        chunks = []
        async for chunk in switch.execute_stream(request):
            chunks.append(chunk)
        end_time = time.time()

        total_time = (end_time - start_time) * 1000

        # Streaming should complete within reasonable time
        assert total_time < fast_provider.latency_ms * 2
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_fallback_latency(self, fast_provider, slow_provider):
        """Test latency when fallback is triggered."""
        # Make fast provider fail
        fast_provider._make_api_call = AsyncMock(
            side_effect=Exception("Fast provider failed")
        )

        switch = LLMSwitch(
            providers={"fast_provider": fast_provider, "slow_provider": slow_provider}
        )

        request = TaskRequest(
            prompt="Fallback test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        start_time = time.time()
        response = await switch.execute_with_fallback(request)
        end_time = time.time()

        total_time = (end_time - start_time) * 1000

        # Should fallback to slow provider
        assert response.provider == "slow"
        assert total_time >= slow_provider.latency_ms - 50  # Allow some tolerance

    def test_provider_selection_latency(self, mixed_providers):
        """Test provider selection algorithm latency."""
        switch = LLMSwitch(providers=mixed_providers)

        request = TaskRequest(
            prompt="Selection test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Measure selection time
        start_time = time.time()
        decision = switch.select_llm(request)
        end_time = time.time()

        selection_time = (end_time - start_time) * 1000

        # Selection should be very fast (< 10ms)
        assert selection_time < 10
        assert decision is not None


class TestThroughputPerformance:
    """Test throughput performance under load."""

    @pytest.fixture
    def high_throughput_provider(self):
        """Create provider optimized for high throughput."""
        return PerformanceTestProvider("high_throughput", latency_ms=50)

    @pytest.mark.asyncio
    async def test_requests_per_second(self, high_throughput_provider):
        """Test requests per second capability."""
        switch = LLMSwitch(
            providers={"high_throughput_provider": high_throughput_provider}
        )

        request = TaskRequest(
            prompt="Throughput test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Run for 2 seconds
        start_time = time.time()
        completed_requests = 0

        while time.time() - start_time < 2.0:
            await switch.execute_with_fallback(request)
            completed_requests += 1

        duration = time.time() - start_time
        rps = completed_requests / duration

        # Should handle at least 10 RPS (conservative estimate)
        assert rps >= 10
        print(f"Achieved {rps:.2f} requests per second")

    @pytest.mark.asyncio
    async def test_concurrent_throughput(self, high_throughput_provider):
        """Test throughput with concurrent requests."""
        switch = LLMSwitch(
            providers={"high_throughput_provider": high_throughput_provider}
        )

        request = TaskRequest(
            prompt="Concurrent throughput test",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Execute 50 concurrent requests
        start_time = time.time()
        tasks = [switch.execute_with_fallback(request) for _ in range(50)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        duration = end_time - start_time
        throughput = len(responses) / duration

        # Should handle concurrent requests efficiently
        assert len(responses) == 50
        assert throughput > 20  # At least 20 RPS with concurrency
        print(f"Achieved {throughput:.2f} concurrent requests per second")

    @pytest.mark.asyncio
    async def test_mixed_workload_throughput(self, mixed_providers):
        """Test throughput with mixed workload."""
        switch = LLMSwitch(providers=mixed_providers)

        # Mix of different request types
        requests = [
            TaskRequest(prompt="Text generation", task_type=TaskType.TEXT_GENERATION),
            TaskRequest(prompt="Code generation", task_type=TaskType.CODE_GENERATION),
            TaskRequest(prompt="Reasoning task", task_type=TaskType.REASONING),
        ]

        start_time = time.time()
        completed_requests = 0

        # Run for 3 seconds with mixed requests
        while time.time() - start_time < 3.0:
            request = requests[completed_requests % len(requests)]
            await switch.execute_with_fallback(request)
            completed_requests += 1

        duration = time.time() - start_time
        throughput = completed_requests / duration

        # Should handle mixed workload
        assert throughput > 5  # Conservative estimate
        print(f"Achieved {throughput:.2f} mixed requests per second")


class TestMemoryPerformance:
    """Test memory usage and efficiency."""

    @pytest.fixture
    def memory_test_provider(self):
        """Create provider for memory testing."""
        return PerformanceTestProvider("memory_test", latency_ms=10)

    def test_memory_usage_single_request(self, memory_test_provider):
        """Test memory usage for single request."""
        switch = LLMSwitch(providers={"memory_test_provider": memory_test_provider})

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Execute single request
        request = TaskRequest(
            prompt="Memory test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Run request synchronously for memory test
        import asyncio

        response = asyncio.run(switch.execute_with_fallback(request))

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50
        assert response is not None

    @pytest.mark.asyncio
    async def test_memory_usage_high_load(self, memory_test_provider):
        """Test memory usage under high load."""
        switch = LLMSwitch(providers={"memory_test_provider": memory_test_provider})

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        request = TaskRequest(
            prompt="High load memory test",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Execute many requests
        for _ in range(100):
            await switch.execute_with_fallback(request)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable even under load
        assert memory_increase < 200  # Allow more memory for high load
        print(f"Memory increase under high load: {memory_increase:.2f} MB")

    def test_cache_memory_usage(self, memory_test_provider):
        """Test memory usage with caching enabled."""
        config = SwitchConfig(enable_caching=True)
        switch = LLMSwitch(
            providers={"memory_test_provider": memory_test_provider}, config=config
        )

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        request = TaskRequest(
            prompt="Cache memory test",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Execute same request multiple times (should use cache)
        import asyncio

        for _ in range(10):
            asyncio.run(switch.execute_with_fallback(request))

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Cache should be memory efficient
        assert memory_increase < 100
        print(f"Memory increase with caching: {memory_increase:.2f} MB")


class TestPerformanceMonitoring:
    """Test performance monitoring capabilities."""

    def test_metrics_collection_performance(self):
        """Test performance of metrics collection."""
        monitor = PerformanceMonitor()

        start_time = time.time()

        # Record many metrics
        for i in range(1000):
            monitor.record_metric("test_metric", i, {"tag": "test"})

        end_time = time.time()
        collection_time = (end_time - start_time) * 1000

        # Metrics collection should be very fast
        assert collection_time < 100  # Less than 100ms for 1000 metrics
        print(f"Metrics collection time: {collection_time:.2f}ms for 1000 metrics")

    def test_metrics_aggregation_performance(self):
        """Test performance of metrics aggregation."""
        monitor = PerformanceMonitor()

        # Record many metrics first
        for i in range(10000):
            monitor.record_metric(
                "aggregation_test", i % 100, {"provider": f"provider_{i % 5}"}
            )

        start_time = time.time()

        # Get aggregated stats
        stats = monitor.get_metric_stats("aggregation_test")

        end_time = time.time()
        aggregation_time = (end_time - start_time) * 1000

        # Aggregation should be fast
        assert aggregation_time < 50  # Less than 50ms
        assert stats.count == 10000
        print(f"Metrics aggregation time: {aggregation_time:.2f}ms for 10000 metrics")

    def test_benchmark_manager_performance(self):
        """Test benchmark manager performance."""
        benchmark_manager = BenchmarkManager()

        start_time = time.time()

        # Get multiple benchmark scores
        for model in ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet"]:
            scores = benchmark_manager.get_benchmark_scores(model)
            ranking = benchmark_manager.get_task_performance_ranking("text_generation")

        end_time = time.time()
        benchmark_time = (end_time - start_time) * 1000

        # Benchmark operations should be fast
        assert benchmark_time < 100  # Less than 100ms
        print(f"Benchmark operations time: {benchmark_time:.2f}ms")


class TestStressTesting:
    """Stress tests for system stability."""

    @pytest.fixture
    def stress_test_provider(self):
        """Create provider for stress testing."""
        return PerformanceTestProvider("stress_test", latency_ms=20, success_rate=0.95)

    @pytest.mark.asyncio
    async def test_prolonged_high_load(self, stress_test_provider):
        """Test system under prolonged high load."""
        switch = LLMSwitch(providers={"stress_test_provider": stress_test_provider})

        request = TaskRequest(
            prompt="Stress test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        start_time = time.time()
        completed_requests = 0
        failed_requests = 0

        # Run for 30 seconds under high load
        while time.time() - start_time < 30:
            try:
                await switch.execute_with_fallback(request)
                completed_requests += 1
            except Exception:
                failed_requests += 1

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)

        duration = time.time() - start_time
        success_rate = completed_requests / (completed_requests + failed_requests)

        # Should maintain high success rate
        assert success_rate >= 0.9  # At least 90% success rate
        assert completed_requests > 100  # Should complete many requests
        print(
            f"Stress test: {completed_requests} requests, {success_rate:.2%} success rate"
        )

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, stress_test_provider):
        """Test for memory leaks under prolonged usage."""
        switch = LLMSwitch(providers={"stress_test_provider": stress_test_provider})

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        request = TaskRequest(
            prompt="Memory leak test",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Run many requests and check memory
        for i in range(500):
            await switch.execute_with_fallback(request)

            # Check memory every 100 requests
            if i % 100 == 0 and i > 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory

                # Memory should not grow unbounded
                assert memory_increase < 500  # Less than 500MB increase
                print(f"Memory after {i} requests: {memory_increase:.2f} MB increase")

    @pytest.mark.asyncio
    async def test_error_recovery_stress(self, stress_test_provider):
        """Test error recovery under stress."""
        # Create provider with high failure rate
        unreliable_provider = PerformanceTestProvider(
            "unreliable", latency_ms=30, success_rate=0.7
        )

        reliable_provider = PerformanceTestProvider(
            "reliable", latency_ms=50, success_rate=1.0
        )

        switch = LLMSwitch(
            providers={
                "unreliable_provider": unreliable_provider,
                "reliable_provider": reliable_provider,
            }
        )

        request = TaskRequest(
            prompt="Error recovery test",
            task_type=TaskType.TEXT_GENERATION,
        )

        completed_requests = 0
        failed_requests = 0

        # Run many requests to test error recovery
        for _ in range(200):
            try:
                await switch.execute_with_fallback(request)
                completed_requests += 1
            except Exception:
                failed_requests += 1

        success_rate = completed_requests / (completed_requests + failed_requests)

        # Should recover from errors and maintain good success rate
        assert success_rate >= 0.8  # At least 80% success with fallback
        print(f"Error recovery test: {success_rate:.2%} success rate")


class TestScalabilityPerformance:
    """Test scalability performance."""

    @pytest.mark.asyncio
    async def test_multiple_providers_scalability(self):
        """Test performance with multiple providers."""
        # Create multiple providers
        providers = {
            f"provider_{i}": PerformanceTestProvider(
                f"provider_{i}", latency_ms=50 + i * 10
            )
            for i in range(10)
        }

        switch = LLMSwitch(providers=providers)

        request = TaskRequest(
            prompt="Scalability test",
            task_type=TaskType.TEXT_GENERATION,
        )

        start_time = time.time()

        # Execute requests with multiple providers
        tasks = [switch.execute_with_fallback(request) for _ in range(20)]
        responses = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Should distribute load across providers
        assert len(responses) == 20
        assert total_time < 2.0  # Should complete within 2 seconds

        # Check that different providers were used
        providers_used = set(r.provider for r in responses)
        assert len(providers_used) > 1  # Should use multiple providers

    def test_large_request_handling(self):
        """Test handling of large requests."""
        switch = LLMSwitch(
            providers={
                "large_request_test": PerformanceTestProvider("large_request_test")
            }
        )

        # Create large request
        large_prompt = "Test prompt " * 1000  # Large prompt
        request = TaskRequest(
            prompt=large_prompt,
            task_type=TaskType.TEXT_GENERATION,
        )

        start_time = time.time()

        # Should handle large requests efficiently
        import asyncio

        response = asyncio.run(switch.execute_with_fallback(request))

        end_time = time.time()
        processing_time = end_time - start_time

        assert response is not None
        assert processing_time < 5.0  # Should complete within 5 seconds
        print(f"Large request processing time: {processing_time:.2f}s")
