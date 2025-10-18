"""
Integration tests for LLM-Dispatcher benchmarks.

This module contains integration tests that test the benchmark system
with real or near-real scenarios.
"""

import pytest
import asyncio
import time
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from llm_dispatcher.benchmarks import (
    PerformanceBenchmark,
    CostBenchmark,
    QualityBenchmark,
    CustomBenchmark,
    BenchmarkRunner,
    BenchmarkAnalyzer,
    BenchmarkReporter,
)
from llm_dispatcher.core.base import TaskRequest, TaskResponse, TaskType
from llm_dispatcher import LLMSwitch


class TestBenchmarkIntegration:
    """Integration tests for benchmark system."""

    @pytest.fixture
    def sample_prompts(self):
        """Sample prompts for testing."""
        return [
            "Write a short story about a robot learning to paint",
            "Explain the concept of machine learning in simple terms",
            "Generate Python code to implement a binary search algorithm",
            "Create a marketing slogan for a new AI product",
            "Summarize the key benefits of renewable energy",
        ]

    @pytest.fixture
    def sample_test_cases(self):
        """Sample test cases for quality benchmarks."""
        return [
            {
                "prompt": "What is the capital of Japan?",
                "expected": "Tokyo",
                "type": "factual",
            },
            {
                "prompt": "Write a haiku about spring",
                "expected": "5-7-5 syllable structure",
                "type": "creative",
            },
            {"prompt": "Solve: 25 * 4 = ?", "expected": "100", "type": "mathematical"},
            {
                "prompt": "What is the largest planet in our solar system?",
                "expected": "Jupiter",
                "type": "factual",
            },
        ]

    @pytest.fixture
    def mock_providers_config(self):
        """Mock provider configuration."""
        return {
            "openai": {
                "api_key": "sk-test-openai-key",
                "models": ["gpt-4", "gpt-3.5-turbo"],
            },
            "anthropic": {
                "api_key": "sk-ant-test-anthropic-key",
                "models": ["claude-3-sonnet", "claude-3-haiku"],
            },
            "google": {
                "api_key": "test-google-key",
                "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
            },
        }

    @pytest.fixture
    def mock_llm_switch(self, mock_providers_config):
        """Create mock LLM switch for testing."""
        switch = MagicMock(spec=LLMSwitch)
        switch.providers = mock_providers_config
        switch.process_request = AsyncMock()
        return switch

    @pytest.mark.asyncio
    async def test_performance_benchmark_integration(
        self, sample_prompts, mock_llm_switch
    ):
        """Test performance benchmark with realistic scenarios."""
        # Mock realistic responses with varying latencies
        responses = [
            TaskResponse(
                content="Once upon a time, there was a robot named ArtBot who discovered the joy of painting...",
                provider="openai",
                model_used="gpt-4",
                tokens_used=150,
                cost=0.045,
                latency_ms=1200,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience...",
                provider="anthropic",
                model_used="claude-3-sonnet",
                tokens_used=200,
                cost=0.038,
                latency_ms=1100,
                finish_reason="stop",
            ),
            TaskResponse(
                content="def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
                provider="google",
                model_used="gemini-2.5-pro",
                tokens_used=180,
                cost=0.025,
                latency_ms=900,
                finish_reason="stop",
            ),
            TaskResponse(
                content="AI-Powered Innovation: Transforming Tomorrow, Today",
                provider="openai",
                model_used="gpt-3.5-turbo",
                tokens_used=50,
                cost=0.015,
                latency_ms=800,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Renewable energy offers numerous benefits including reduced greenhouse gas emissions, energy independence, and long-term cost savings...",
                provider="anthropic",
                model_used="claude-3-haiku",
                tokens_used=120,
                cost=0.022,
                latency_ms=700,
                finish_reason="stop",
            ),
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Create performance benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts,
            iterations=2,
            concurrent_requests=3,
            switch=mock_llm_switch,
        )

        # Run benchmark
        results = await benchmark.run()

        # Verify results
        assert results is not None
        assert results.avg_latency > 0
        assert results.throughput > 0
        assert results.success_rate > 0
        assert len(results.provider_metrics) > 0

        # Verify provider-specific metrics
        for provider in ["openai", "anthropic", "google"]:
            assert provider in results.provider_metrics
            provider_metrics = results.provider_metrics[provider]
            assert provider_metrics.avg_latency > 0
            assert provider_metrics.requests > 0

    @pytest.mark.asyncio
    async def test_cost_benchmark_integration(self, sample_prompts, mock_llm_switch):
        """Test cost benchmark with realistic cost scenarios."""
        # Mock responses with realistic costs
        responses = [
            TaskResponse(
                content="Story content...",
                provider="openai",
                model_used="gpt-4",
                tokens_used=200,
                cost=0.06,  # Higher cost for GPT-4
                latency_ms=1200,
                finish_reason="stop",
            ),
            TaskResponse(
                content="ML explanation...",
                provider="anthropic",
                model_used="claude-3-sonnet",
                tokens_used=180,
                cost=0.034,  # Medium cost for Claude
                latency_ms=1100,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Code content...",
                provider="google",
                model_used="gemini-2.5-pro",
                tokens_used=220,
                cost=0.028,  # Lower cost for Gemini
                latency_ms=900,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Slogan content...",
                provider="openai",
                model_used="gpt-3.5-turbo",
                tokens_used=80,
                cost=0.012,  # Lower cost for GPT-3.5
                latency_ms=800,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Summary content...",
                provider="anthropic",
                model_used="claude-3-haiku",
                tokens_used=150,
                cost=0.027,  # Medium cost for Claude Haiku
                latency_ms=700,
                finish_reason="stop",
            ),
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Create cost benchmark
        benchmark = CostBenchmark(
            test_prompts=sample_prompts, iterations=2, switch=mock_llm_switch
        )

        # Run benchmark
        results = await benchmark.run()

        # Verify results
        assert results is not None
        assert results.avg_cost > 0
        assert results.total_cost > 0
        assert results.cost_per_token > 0

        # Verify cost analysis
        assert (
            results.total_cost > results.avg_cost
        )  # Total should be higher than average
        assert results.cost_per_token > 0

        # Verify provider cost comparison
        for provider in ["openai", "anthropic", "google"]:
            assert provider in results.provider_metrics
            provider_metrics = results.provider_metrics[provider]
            assert provider_metrics.avg_cost > 0
            assert provider_metrics.total_cost > 0

    @pytest.mark.asyncio
    async def test_quality_benchmark_integration(
        self, sample_test_cases, mock_llm_switch
    ):
        """Test quality benchmark with realistic quality scenarios."""
        # Mock responses with varying quality
        responses = [
            TaskResponse(
                content="Tokyo",
                provider="openai",
                model_used="gpt-4",
                tokens_used=10,
                cost=0.003,
                latency_ms=500,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Cherry blossoms bloom\nGentle breeze through ancient trees\nNature's peaceful song",
                provider="anthropic",
                model_used="claude-3-sonnet",
                tokens_used=25,
                cost=0.005,
                latency_ms=800,
                finish_reason="stop",
            ),
            TaskResponse(
                content="100",
                provider="google",
                model_used="gemini-2.5-pro",
                tokens_used=5,
                cost=0.001,
                latency_ms=300,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Jupiter",
                provider="openai",
                model_used="gpt-3.5-turbo",
                tokens_used=8,
                cost=0.002,
                latency_ms=400,
                finish_reason="stop",
            ),
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Create quality benchmark
        benchmark = QualityBenchmark(
            test_cases=sample_test_cases, iterations=2, switch=mock_llm_switch
        )

        # Run benchmark
        results = await benchmark.run()

        # Verify results
        assert results is not None
        assert results.accuracy > 0
        assert results.quality_score > 0
        assert len(results.test_case_results) == len(sample_test_cases)

        # Verify accuracy by type
        assert "factual" in results.accuracy_by_type
        assert "creative" in results.accuracy_by_type
        assert "mathematical" in results.accuracy_by_type

        # Verify test case results
        for test_case_result in results.test_case_results:
            assert test_case_result.prompt is not None
            assert test_case_result.expected is not None
            assert test_case_result.actual is not None
            assert test_case_result.score >= 0
            assert test_case_result.score <= 1

    @pytest.mark.asyncio
    async def test_custom_benchmark_integration(self, mock_llm_switch):
        """Test custom benchmark with custom evaluation logic."""

        # Define custom evaluator
        def custom_evaluator(response: str, expected: str) -> float:
            """Custom evaluation function that checks for keyword presence."""
            response_lower = response.lower()
            expected_lower = expected.lower()

            if expected_lower in response_lower:
                return 1.0
            elif any(word in response_lower for word in expected_lower.split()):
                return 0.7
            else:
                return 0.2

        # Custom test cases
        custom_test_cases = [
            {
                "prompt": "What is artificial intelligence?",
                "expected": "artificial intelligence",
                "evaluator": custom_evaluator,
            },
            {
                "prompt": "Explain machine learning",
                "expected": "machine learning algorithms",
                "evaluator": custom_evaluator,
            },
            {
                "prompt": "What is deep learning?",
                "expected": "neural networks",
                "evaluator": custom_evaluator,
            },
        ]

        # Mock responses
        responses = [
            TaskResponse(
                content="Artificial intelligence is the simulation of human intelligence in machines",
                provider="openai",
                model_used="gpt-4",
                tokens_used=30,
                cost=0.009,
                latency_ms=600,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Machine learning involves algorithms that can learn from data",
                provider="anthropic",
                model_used="claude-3-sonnet",
                tokens_used=25,
                cost=0.005,
                latency_ms=700,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Deep learning uses neural networks with multiple layers",
                provider="google",
                model_used="gemini-2.5-pro",
                tokens_used=28,
                cost=0.004,
                latency_ms=500,
                finish_reason="stop",
            ),
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Create custom benchmark
        benchmark = CustomBenchmark(
            test_cases=custom_test_cases, iterations=2, switch=mock_llm_switch
        )

        # Run benchmark
        results = await benchmark.run()

        # Verify results
        assert results is not None
        assert results.custom_score > 0
        assert len(results.test_case_results) == len(custom_test_cases)

        # Verify custom evaluation worked
        for test_case_result in results.test_case_results:
            assert test_case_result.score >= 0
            assert test_case_result.score <= 1

    @pytest.mark.asyncio
    async def test_comprehensive_benchmark_integration(
        self, sample_prompts, sample_test_cases, mock_llm_switch
    ):
        """Test comprehensive benchmark that runs all benchmark types."""
        # Mock responses for comprehensive test
        responses = []

        # Performance test responses
        for prompt in sample_prompts:
            responses.append(
                TaskResponse(
                    content=f"Response for: {prompt[:50]}...",
                    provider="openai",
                    model_used="gpt-4",
                    tokens_used=100,
                    cost=0.03,
                    latency_ms=1000,
                )
            )

        # Quality test responses
        for test_case in sample_test_cases:
            responses.append(
                TaskResponse(
                    content=test_case["expected"],
                    provider="anthropic",
                    model_used="claude-3-sonnet",
                    tokens_used=20,
                    cost=0.004,
                    latency_ms=600,
                )
            )

        mock_llm_switch.process_request.side_effect = responses

        # Create benchmark runner
        runner = BenchmarkRunner(switch=mock_llm_switch)

        # Run comprehensive benchmark
        results = await runner.run_comprehensive_benchmark(
            providers=["openai", "anthropic", "google"],
            models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
            test_prompts=sample_prompts,
            test_cases=sample_test_cases,
            iterations=1,
        )

        # Verify comprehensive results
        assert results is not None
        assert results.performance is not None
        assert results.cost is not None
        assert results.quality is not None

        # Verify performance results
        assert results.performance.avg_latency > 0
        assert results.performance.throughput > 0
        assert results.performance.success_rate > 0

        # Verify cost results
        assert results.cost.avg_cost > 0
        assert results.cost.total_cost > 0
        assert results.cost.cost_per_token > 0

        # Verify quality results
        assert results.quality.accuracy > 0
        assert results.quality.quality_score > 0

    @pytest.mark.asyncio
    async def test_benchmark_analysis_integration(
        self, sample_prompts, mock_llm_switch
    ):
        """Test benchmark analysis and reporting integration."""
        # Mock responses
        responses = [
            TaskResponse(
                content="Test response",
                provider="openai",
                model_used="gpt-4",
                tokens_used=100,
                cost=0.03,
                latency_ms=1000,
                finish_reason="stop",
            )
            for _ in range(len(sample_prompts) * 2)  # 2 iterations
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Run benchmark
        runner = BenchmarkRunner(switch=mock_llm_switch)
        results = await runner.run_performance_benchmark(
            providers=["openai"], models=["gpt-4"], test_prompts=sample_prompts
        )

        # Analyze results
        analyzer = BenchmarkAnalyzer(results)
        stats = analyzer.get_statistical_analysis()
        comparison = analyzer.compare_providers()
        trends = analyzer.get_trend_analysis()

        # Verify analysis
        assert stats is not None
        assert comparison is not None
        assert trends is not None

        # Verify statistical analysis
        assert hasattr(stats, "latency")
        assert hasattr(stats, "cost")
        assert hasattr(stats, "quality")

        # Verify provider comparison
        assert isinstance(comparison, dict)
        assert "openai" in comparison

        # Verify trend analysis
        assert isinstance(trends, dict)

    @pytest.mark.asyncio
    async def test_benchmark_reporting_integration(
        self, sample_prompts, mock_llm_switch, tmp_path
    ):
        """Test benchmark reporting integration."""
        # Mock responses
        responses = [
            TaskResponse(
                content="Test response",
                provider="openai",
                model_used="gpt-4",
                tokens_used=100,
                cost=0.03,
                latency_ms=1000,
                finish_reason="stop",
            )
            for _ in range(len(sample_prompts) * 2)
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Run benchmark
        runner = BenchmarkRunner(switch=mock_llm_switch)
        results = await runner.run_performance_benchmark(
            providers=["openai"], models=["gpt-4"], test_prompts=sample_prompts
        )

        # Generate reports
        reporter = BenchmarkReporter(results)

        # Test HTML report
        html_file = tmp_path / "benchmark_report.html"
        html_result = reporter.generate_html_report(str(html_file))
        assert html_result is not None
        assert html_file.exists()

        # Test JSON report
        json_file = tmp_path / "benchmark_report.json"
        json_result = reporter.generate_json_report(str(json_file))
        assert json_result is not None
        assert json_file.exists()

        # Test CSV report
        csv_file = tmp_path / "benchmark_report.csv"
        csv_result = reporter.generate_csv_report(str(csv_file))
        assert csv_result is not None
        assert csv_file.exists()

        # Test custom report
        custom_file = tmp_path / "custom_report.html"
        custom_result = reporter.generate_custom_report(
            template="basic_template", output_file=str(custom_file), include_charts=True
        )
        assert custom_result is not None
        assert custom_file.exists()

    @pytest.mark.asyncio
    async def test_benchmark_error_handling_integration(
        self, sample_prompts, mock_llm_switch
    ):
        """Test benchmark error handling in realistic scenarios."""

        # Mock mixed success/failure responses
        def mixed_responses(*args, **kwargs):
            # Fail every 3rd request
            if not hasattr(mixed_responses, "call_count"):
                mixed_responses.call_count = 0
            mixed_responses.call_count += 1

            if mixed_responses.call_count % 3 == 0:
                raise Exception("Simulated API error")

            return TaskResponse(
                content="Successful response",
                provider="openai",
                model_used="gpt-4",
                tokens_used=100,
                cost=0.03,
                latency_ms=1000,
                finish_reason="stop",
            )

        mock_llm_switch.process_request.side_effect = mixed_responses

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts, iterations=2, switch=mock_llm_switch
        )

        # Run benchmark (should handle errors gracefully)
        results = await benchmark.run()

        # Verify error handling
        assert results is not None
        assert results.success_rate < 1.0
        assert results.error_count > 0
        assert results.error_count < results.total_requests

    @pytest.mark.asyncio
    async def test_benchmark_concurrent_execution(
        self, sample_prompts, mock_llm_switch
    ):
        """Test benchmark with concurrent execution."""

        # Mock responses with delays to test concurrency
        async def delayed_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return TaskResponse(
                content="Delayed response",
                provider="openai",
                model_used="gpt-4",
                tokens_used=100,
                cost=0.03,
                latency_ms=100,
                finish_reason="stop",
            )

        mock_llm_switch.process_request.side_effect = delayed_response

        # Create benchmark with high concurrency
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts[:3],  # Use fewer prompts
            iterations=2,
            concurrent_requests=5,  # High concurrency
            switch=mock_llm_switch,
        )

        # Measure execution time
        start_time = time.time()
        results = await benchmark.run()
        end_time = time.time()

        # Verify results
        assert results is not None
        assert results.success_rate > 0

        # Verify concurrency worked (should be faster than sequential)
        execution_time = end_time - start_time
        # With 3 prompts, 2 iterations, 5 concurrent requests = 6 total requests
        # Sequential would take at least 6 * 0.1 = 0.6 seconds
        # Concurrent should be much faster
        assert execution_time < 0.5  # Should be significantly faster

    @pytest.mark.asyncio
    async def test_benchmark_memory_usage(self, sample_prompts, mock_llm_switch):
        """Test benchmark memory usage with large datasets."""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Mock responses
        responses = [
            TaskResponse(
                content="Test response " * 1000,  # Large response
                provider="openai",
                model_used="gpt-4",
                tokens_used=1000,
                cost=0.3,
                latency_ms=1000,
                finish_reason="stop",
            )
            for _ in range(len(sample_prompts) * 10)  # Many iterations
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Create benchmark with many iterations
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts, iterations=10, switch=mock_llm_switch
        )

        # Run benchmark
        results = await benchmark.run()

        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Verify results
        assert results is not None
        assert results.success_rate > 0

        # Verify memory usage is reasonable (less than 100MB increase)
        assert memory_increase < 100 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_benchmark_provider_comparison(self, sample_prompts, mock_llm_switch):
        """Test benchmark provider comparison functionality."""
        # Mock responses from different providers with different characteristics
        responses = [
            # OpenAI responses (higher cost, medium latency)
            TaskResponse(
                content="OpenAI response",
                provider="openai",
                model_used="gpt-4",
                tokens_used=100,
                cost=0.03,
                latency_ms=1200,
                finish_reason="stop",
            ),
            # Anthropic responses (medium cost, high latency)
            TaskResponse(
                content="Anthropic response",
                provider="anthropic",
                model_used="claude-3-sonnet",
                tokens_used=100,
                cost=0.025,
                latency_ms=1400,
                finish_reason="stop",
            ),
            # Google responses (lower cost, low latency)
            TaskResponse(
                content="Google response",
                provider="google",
                model_used="gemini-2.5-pro",
                tokens_used=100,
                cost=0.02,
                latency_ms=800,
                finish_reason="stop",
            ),
        ]

        mock_llm_switch.process_request.side_effect = responses

        # Create benchmark
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts[:3],  # Use fewer prompts
            iterations=2,
            switch=mock_llm_switch,
        )

        # Run benchmark
        results = await benchmark.run()

        # Verify provider comparison
        assert results is not None
        assert len(results.provider_metrics) == 3

        # Verify each provider has metrics
        for provider in ["openai", "anthropic", "google"]:
            assert provider in results.provider_metrics
            provider_metrics = results.provider_metrics[provider]
            assert provider_metrics.avg_latency > 0
            assert provider_metrics.avg_cost > 0
            assert provider_metrics.requests > 0

        # Verify cost comparison (Google should be cheapest)
        google_cost = results.provider_metrics["google"].avg_cost
        openai_cost = results.provider_metrics["openai"].avg_cost
        anthropic_cost = results.provider_metrics["anthropic"].avg_cost

        assert google_cost < openai_cost
        assert google_cost < anthropic_cost

        # Verify latency comparison (Google should be fastest)
        google_latency = results.provider_metrics["google"].avg_latency
        openai_latency = results.provider_metrics["openai"].avg_latency
        anthropic_latency = results.provider_metrics["anthropic"].avg_latency

        assert google_latency < openai_latency
        assert google_latency < anthropic_latency


if __name__ == "__main__":
    pytest.main([__file__])
