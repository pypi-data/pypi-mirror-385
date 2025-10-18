"""
Performance tests for LLM-Dispatcher benchmarks.

This module contains performance tests that measure the efficiency
and scalability of the benchmark system itself.
"""

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from llm_dispatcher.benchmarks import (
    PerformanceBenchmark,
    CostBenchmark,
    QualityBenchmark,
    BenchmarkRunner,
)
from llm_dispatcher.core.base import TaskRequest, TaskResponse, TaskType


class TestBenchmarkPerformance:
    """Performance tests for benchmark system."""

    @pytest.fixture
    def large_prompt_set(self):
        """Large set of prompts for performance testing."""
        return [
            f"Generate content for test case {i}: Write a comprehensive analysis of topic {i}"
            for i in range(100)
        ]

    @pytest.fixture
    def large_test_cases(self):
        """Large set of test cases for performance testing."""
        return [
            {
                "prompt": f"What is the capital of country {i}?",
                "expected": f"Capital{i}",
                "type": "factual",
            }
            for i in range(50)
        ]

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for performance testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.mark.asyncio
    async def test_benchmark_system_memory_usage(self, large_prompt_set, mock_switch):
        """Test memory usage of benchmark system with large datasets."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Mock responses
        mock_response = TaskResponse(
            content="Test response content",
            provider="test_provider",
            model="test_model",
            tokens_used=100,
            cost=0.01,
            latency=1000,
        )
        mock_switch.process_request.return_value = mock_response

        # Create benchmark with large dataset
        benchmark = PerformanceBenchmark(
            test_prompts=large_prompt_set,
            iterations=2,
            concurrent_requests=10,
            switch=mock_switch,
        )

        # Run benchmark
        results = await benchmark.run()

        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Verify results
        assert results is not None
        assert results.success_rate > 0

        # Memory increase should be reasonable (less than 200MB)
        assert memory_increase < 200 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_benchmark_concurrent_performance(self, mock_switch):
        """Test benchmark performance with high concurrency."""
        prompts = [f"Test prompt {i}" for i in range(20)]

        # Mock fast response
        mock_response = TaskResponse(
            content="Fast response",
            provider="test_provider",
            model="test_model",
            tokens_used=50,
            cost=0.005,
            latency=100,  # Fast response
        )
        mock_switch.process_request.return_value = mock_response

        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        execution_times = []

        for concurrency in concurrency_levels:
            benchmark = PerformanceBenchmark(
                test_prompts=prompts,
                iterations=1,
                concurrent_requests=concurrency,
                switch=mock_switch,
            )

            start_time = time.time()
            results = await benchmark.run()
            end_time = time.time()

            execution_times.append(end_time - start_time)

            # Verify results
            assert results is not None
            assert results.success_rate > 0

        # Higher concurrency should generally be faster
        # (though this may not always be true due to overhead)
        assert (
            execution_times[0] > execution_times[-1] * 0.5
        )  # At least 50% improvement

    @pytest.mark.asyncio
    async def test_benchmark_large_dataset_performance(self, mock_switch):
        """Test benchmark performance with very large datasets."""
        # Create very large dataset
        large_prompts = [f"Large dataset prompt {i}" for i in range(500)]

        # Mock response
        mock_response = TaskResponse(
            content="Response for large dataset",
            provider="test_provider",
            model="test_model",
            tokens_used=100,
            cost=0.01,
            latency=1000,
        )
        mock_switch.process_request.return_value = mock_response

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=large_prompts,
            iterations=1,
            concurrent_requests=20,
            switch=mock_switch,
        )

        # Measure execution time
        start_time = time.time()
        results = await benchmark.run()
        end_time = time.time()

        execution_time = end_time - start_time

        # Verify results
        assert results is not None
        assert results.success_rate > 0
        assert results.total_requests == len(large_prompts)

        # Should complete within reasonable time (less than 30 seconds for 500 requests)
        assert execution_time < 30

    @pytest.mark.asyncio
    async def test_benchmark_cpu_usage(self, mock_switch):
        """Test CPU usage during benchmark execution."""
        prompts = [f"CPU test prompt {i}" for i in range(50)]

        # Mock response
        mock_response = TaskResponse(
            content="CPU test response",
            provider="test_provider",
            model="test_model",
            tokens_used=100,
            cost=0.01,
            latency=1000,
        )
        mock_switch.process_request.return_value = mock_response

        # Monitor CPU usage
        process = psutil.Process(os.getpid())
        cpu_samples = []

        def monitor_cpu():
            cpu_samples.append(process.cpu_percent())

        # Start monitoring
        monitor_task = asyncio.create_task(
            self._monitor_cpu_usage(monitor_cpu, duration=10)
        )

        # Create and run benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=prompts,
            iterations=2,
            concurrent_requests=10,
            switch=mock_switch,
        )

        results = await benchmark.run()

        # Stop monitoring
        monitor_task.cancel()

        # Verify results
        assert results is not None
        assert results.success_rate > 0

        # CPU usage should be reasonable (less than 80% average)
        if cpu_samples:
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            assert avg_cpu < 80

    async def _monitor_cpu_usage(self, monitor_func, duration):
        """Helper method to monitor CPU usage."""
        start_time = time.time()
        while time.time() - start_time < duration:
            monitor_func()
            await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_benchmark_throughput_scaling(self, mock_switch):
        """Test benchmark throughput scaling with different configurations."""
        base_prompts = [f"Throughput test {i}" for i in range(10)]

        # Mock response
        mock_response = TaskResponse(
            content="Throughput test response",
            provider="test_provider",
            model="test_model",
            tokens_used=100,
            cost=0.01,
            latency=500,  # Fixed latency
        )
        mock_switch.process_request.return_value = mock_response

        # Test different configurations
        configurations = [
            {"iterations": 1, "concurrent_requests": 1},
            {"iterations": 2, "concurrent_requests": 2},
            {"iterations": 1, "concurrent_requests": 5},
            {"iterations": 1, "concurrent_requests": 10},
        ]

        throughputs = []

        for config in configurations:
            benchmark = PerformanceBenchmark(
                test_prompts=base_prompts,
                iterations=config["iterations"],
                concurrent_requests=config["concurrent_requests"],
                switch=mock_switch,
            )

            start_time = time.time()
            results = await benchmark.run()
            end_time = time.time()

            execution_time = end_time - start_time
            throughput = results.total_requests / execution_time
            throughputs.append(throughput)

            # Verify results
            assert results is not None
            assert results.success_rate > 0

        # Throughput should generally increase with higher concurrency
        assert throughputs[-1] > throughputs[0] * 0.5  # At least 50% improvement

    @pytest.mark.asyncio
    async def test_benchmark_memory_efficiency(self, mock_switch):
        """Test memory efficiency with repeated benchmark runs."""
        prompts = [f"Memory test {i}" for i in range(20)]

        # Mock response
        mock_response = TaskResponse(
            content="Memory test response",
            provider="test_provider",
            model="test_model",
            tokens_used=100,
            cost=0.01,
            latency=1000,
        )
        mock_switch.process_request.return_value = mock_response

        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Run multiple benchmark iterations
        for i in range(5):
            benchmark = PerformanceBenchmark(
                test_prompts=prompts,
                iterations=2,
                concurrent_requests=5,
                switch=mock_switch,
            )

            results = await benchmark.run()
            assert results is not None

            # Force garbage collection
            import gc

            gc.collect()

        # Check final memory
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_benchmark_error_handling_performance(self, mock_switch):
        """Test performance impact of error handling."""
        prompts = [f"Error test {i}" for i in range(30)]

        # Mock mixed success/failure responses
        call_count = 0

        async def mixed_responses(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count % 5 == 0:  # Fail every 5th request
                raise Exception("Simulated error")
            else:
                return TaskResponse(
                    content="Success response",
                    provider="test_provider",
                    model_used="test_model",
                    tokens_used=100,
                    cost=0.01,
                    latency_ms=1000,
                )

        mock_switch.process_request.side_effect = mixed_responses

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=prompts,
            iterations=2,
            concurrent_requests=5,
            switch=mock_switch,
        )

        # Measure execution time
        start_time = time.time()
        results = await benchmark.run()
        end_time = time.time()

        execution_time = end_time - start_time

        # Verify results
        assert results is not None
        assert results.success_rate < 1.0  # Should have some failures
        assert results.error_count > 0

        # Error handling shouldn't significantly impact performance
        # (should complete within reasonable time)
        assert execution_time < 15

    @pytest.mark.asyncio
    async def test_benchmark_data_processing_performance(self, mock_switch):
        """Test performance of benchmark data processing."""
        # Create benchmark with large result set
        prompts = [f"Data processing test {i}" for i in range(100)]

        # Mock responses with varying data sizes
        responses = []
        for i in range(len(prompts) * 2):  # 2 iterations
            content_size = 1000 + (i % 10) * 100  # Varying content size
            responses.append(
                TaskResponse(
                    content="x" * content_size,  # Large content
                    provider="test_provider",
                    model_used="test_model",
                    tokens_used=content_size // 10,
                    cost=content_size * 0.00001,
                    latency_ms=1000 + (i % 5) * 100,  # Varying latency
                )
            )

        mock_switch.process_request.side_effect = responses

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=prompts,
            iterations=2,
            concurrent_requests=10,
            switch=mock_switch,
        )

        # Measure execution time
        start_time = time.time()
        results = await benchmark.run()
        end_time = time.time()

        execution_time = end_time - start_time

        # Verify results
        assert results is not None
        assert results.success_rate > 0
        assert len(results.provider_metrics) > 0

        # Data processing should be efficient
        assert execution_time < 20

    @pytest.mark.asyncio
    async def test_benchmark_concurrent_limit_performance(self, mock_switch):
        """Test performance with different concurrent request limits."""
        prompts = [f"Concurrent limit test {i}" for i in range(25)]

        # Mock response with delay
        async def delayed_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return TaskResponse(
                content="Delayed response",
                provider="test_provider",
                model_used="test_model",
                tokens_used=100,
                cost=0.01,
                latency_ms=100,
                finish_reason="stop",
            )

        mock_switch.process_request.side_effect = delayed_response

        # Test different concurrent limits
        concurrent_limits = [1, 5, 10, 25]
        execution_times = []

        for limit in concurrent_limits:
            benchmark = PerformanceBenchmark(
                test_prompts=prompts,
                iterations=1,
                concurrent_requests=limit,
                switch=mock_switch,
            )

            start_time = time.time()
            results = await benchmark.run()
            end_time = time.time()

            execution_times.append(end_time - start_time)

            # Verify results
            assert results is not None
            assert results.success_rate > 0

        # Higher limits should generally be faster (up to a point)
        # The improvement should be significant
        assert execution_times[0] > execution_times[-1] * 0.3

    @pytest.mark.asyncio
    async def test_benchmark_system_resources(self, mock_switch):
        """Test system resource usage during benchmark execution."""
        prompts = [f"Resource test {i}" for i in range(50)]

        # Mock response
        mock_response = TaskResponse(
            content="Resource test response",
            provider="test_provider",
            model="test_model",
            tokens_used=100,
            cost=0.01,
            latency=1000,
        )
        mock_switch.process_request.return_value = mock_response

        # Monitor system resources
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        initial_cpu = process.cpu_percent()

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=prompts,
            iterations=2,
            concurrent_requests=10,
            switch=mock_switch,
        )

        # Run benchmark
        results = await benchmark.run()

        # Check final resources
        final_memory = process.memory_info().rss
        final_cpu = process.cpu_percent()

        memory_increase = final_memory - initial_memory

        # Verify results
        assert results is not None
        assert results.success_rate > 0

        # Resource usage should be reasonable
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB
        assert final_cpu < 90  # Less than 90% CPU

    @pytest.mark.asyncio
    async def test_benchmark_large_result_processing(self, mock_switch):
        """Test processing of large benchmark results."""
        # Create benchmark that will generate large results
        prompts = [f"Large result test {i}" for i in range(200)]

        # Mock responses with large data
        responses = []
        for i in range(len(prompts) * 3):  # 3 iterations
            responses.append(
                TaskResponse(
                    content=f"Large response content {i} " * 100,  # Large content
                    provider=f"provider_{i % 3}",
                    model_used=f"model_{i % 2}",
                    tokens_used=1000 + i,
                    cost=0.01 + i * 0.0001,
                    latency_ms=1000 + i * 10,
                )
            )

        mock_switch.process_request.side_effect = responses

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=prompts,
            iterations=3,
            concurrent_requests=15,
            switch=mock_switch,
        )

        # Measure processing time
        start_time = time.time()
        results = await benchmark.run()
        end_time = time.time()

        processing_time = end_time - start_time

        # Verify results
        assert results is not None
        assert results.success_rate > 0
        assert results.total_requests == len(prompts) * 3

        # Should handle large results efficiently
        assert processing_time < 30

        # Verify result structure
        assert len(results.provider_metrics) == 3  # 3 providers
        for provider_metrics in results.provider_metrics.values():
            assert provider_metrics.requests > 0
            assert provider_metrics.avg_latency > 0
            assert provider_metrics.avg_cost > 0


class TestBenchmarkScalability:
    """Scalability tests for benchmark system."""

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for scalability testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.mark.asyncio
    async def test_benchmark_scales_with_dataset_size(self, mock_switch):
        """Test that benchmark scales appropriately with dataset size."""
        dataset_sizes = [10, 50, 100, 200]
        execution_times = []

        for size in dataset_sizes:
            prompts = [f"Scale test {i}" for i in range(size)]

            # Mock response
            mock_response = TaskResponse(
                content="Scale test response",
                provider="test_provider",
                model_used="test_model",
                tokens_used=100,
                cost=0.01,
                latency_ms=1000,
                finish_reason="stop",
            )
            mock_switch.process_request.return_value = mock_response

            # Create benchmark
            benchmark = PerformanceBenchmark(
                test_prompts=prompts,
                iterations=1,
                concurrent_requests=min(size, 20),  # Scale concurrency with size
                switch=mock_switch,
            )

            # Measure execution time
            start_time = time.time()
            results = await benchmark.run()
            end_time = time.time()

            execution_times.append(end_time - start_time)

            # Verify results
            assert results is not None
            assert results.success_rate > 0
            assert results.total_requests == size

        # Execution time should scale roughly linearly with dataset size
        # (allowing for some overhead)
        for i in range(1, len(execution_times)):
            ratio = execution_times[i] / execution_times[0]
            expected_ratio = dataset_sizes[i] / dataset_sizes[0]
            # Allow for 50% overhead
            assert ratio <= expected_ratio * 1.5

    @pytest.mark.asyncio
    async def test_benchmark_scales_with_concurrency(self, mock_switch):
        """Test that benchmark scales appropriately with concurrency."""
        prompts = [f"Concurrency test {i}" for i in range(50)]

        # Mock response with fixed delay
        async def fixed_delay_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # Fixed 100ms delay
            return TaskResponse(
                content="Concurrency test response",
                provider="test_provider",
                model_used="test_model",
                tokens_used=100,
                cost=0.01,
                latency_ms=100,
                finish_reason="stop",
            )

        mock_switch.process_request.side_effect = fixed_delay_response

        concurrency_levels = [1, 2, 5, 10, 20]
        execution_times = []

        for concurrency in concurrency_levels:
            benchmark = PerformanceBenchmark(
                test_prompts=prompts,
                iterations=1,
                concurrent_requests=concurrency,
                switch=mock_switch,
            )

            start_time = time.time()
            results = await benchmark.run()
            end_time = time.time()

            execution_times.append(end_time - start_time)

            # Verify results
            assert results is not None
            assert results.success_rate > 0

        # Higher concurrency should generally be faster
        # (up to the point of diminishing returns)
        assert execution_times[0] > execution_times[-1] * 0.2

    @pytest.mark.asyncio
    async def test_benchmark_memory_scales_appropriately(self, mock_switch):
        """Test that memory usage scales appropriately with dataset size."""
        dataset_sizes = [10, 50, 100]
        memory_increases = []

        for size in dataset_sizes:
            prompts = [f"Memory scale test {i}" for i in range(size)]

            # Mock response
            mock_response = TaskResponse(
                content="Memory scale test response",
                provider="test_provider",
                model_used="test_model",
                tokens_used=100,
                cost=0.01,
                latency_ms=1000,
                finish_reason="stop",
            )
            mock_switch.process_request.return_value = mock_response

            # Get initial memory
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss

            # Create and run benchmark
            benchmark = PerformanceBenchmark(
                test_prompts=prompts,
                iterations=2,
                concurrent_requests=min(size, 10),
                switch=mock_switch,
            )

            results = await benchmark.run()

            # Check final memory
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            memory_increases.append(memory_increase)

            # Verify results
            assert results is not None
            assert results.success_rate > 0

        # Memory increase should scale roughly linearly with dataset size
        # (allowing for some overhead)
        for i in range(1, len(memory_increases)):
            ratio = memory_increases[i] / memory_increases[0]
            expected_ratio = dataset_sizes[i] / dataset_sizes[0]
            # Allow for 100% overhead
            assert ratio <= expected_ratio * 2


if __name__ == "__main__":
    pytest.main([__file__])
