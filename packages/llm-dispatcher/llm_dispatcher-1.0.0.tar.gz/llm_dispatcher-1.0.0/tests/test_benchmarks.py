"""
Test cases for LLM-Dispatcher benchmarks.

This module contains comprehensive test cases for all benchmark functionality
including performance, cost, quality, and custom benchmarks.
"""

import pytest
import asyncio
import time
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
from llm_dispatcher.exceptions import BenchmarkError


class TestPerformanceBenchmark:
    """Test cases for PerformanceBenchmark."""

    @pytest.fixture
    def sample_prompts(self):
        """Sample test prompts."""
        return [
            "Write a short story about a robot",
            "Explain quantum computing",
            "Generate Python code for sorting",
            "Create a marketing slogan",
            "Summarize the benefits of AI",
        ]

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.fixture
    def performance_benchmark(self, sample_prompts, mock_switch):
        """Create performance benchmark instance."""
        return PerformanceBenchmark(
            test_prompts=sample_prompts,
            iterations=3,
            concurrent_requests=2,
            switch=mock_switch,
        )

    @pytest.mark.asyncio
    async def test_performance_benchmark_initialization(self, performance_benchmark):
        """Test performance benchmark initialization."""
        assert performance_benchmark.test_prompts is not None
        assert len(performance_benchmark.test_prompts) == 5
        assert performance_benchmark.iterations == 3
        assert performance_benchmark.concurrent_requests == 2

    @pytest.mark.asyncio
    async def test_performance_benchmark_run_success(
        self, performance_benchmark, mock_switch
    ):
        """Test successful performance benchmark run."""
        # Mock successful responses
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        results = await performance_benchmark.run()

        assert results is not None
        assert results.avg_latency > 0
        assert results.throughput > 0
        assert results.success_rate == 1.0
        assert len(results.provider_metrics) > 0

    @pytest.mark.asyncio
    async def test_performance_benchmark_with_failures(
        self, performance_benchmark, mock_switch
    ):
        """Test performance benchmark with some failures."""
        # Mock some failures
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )

        def side_effect(*args, **kwargs):
            # Fail every 3rd request
            if hasattr(side_effect, "call_count"):
                side_effect.call_count += 1
            else:
                side_effect.call_count = 1

            if side_effect.call_count % 3 == 0:
                raise Exception("Simulated failure")
            return mock_response

        mock_switch.process_request.side_effect = side_effect

        results = await performance_benchmark.run()

        assert results is not None
        assert results.success_rate < 1.0
        assert results.error_count > 0

    @pytest.mark.asyncio
    async def test_performance_benchmark_concurrent_requests(
        self, sample_prompts, mock_switch
    ):
        """Test performance benchmark with concurrent requests."""
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts[:2],  # Use fewer prompts for faster testing
            iterations=2,
            concurrent_requests=3,
        )

        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        start_time = time.time()
        results = await benchmark.run()
        end_time = time.time()

        # Should complete faster with concurrent requests
        assert results is not None
        assert results.throughput > 0

    @pytest.mark.asyncio
    async def test_performance_benchmark_timeout(self, sample_prompts, mock_switch):
        """Test performance benchmark with timeout."""
        benchmark = PerformanceBenchmark(
            test_prompts=sample_prompts[:1],
            iterations=1,
            timeout=1000,  # 1 second timeout
        )

        # Mock slow response
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(2)  # 2 seconds, should timeout
            return TaskResponse(
                content="Test response",
                provider="test_provider",
                model_used="test_model",
                tokens_used=100,
                cost=0.01,
                latency_ms=2000,
                finish_reason="stop",
            )

        mock_switch.process_request.side_effect = slow_response

        with pytest.raises(BenchmarkError, match="Timeout"):
            await benchmark.run()

    def test_performance_benchmark_validation(self):
        """Test performance benchmark input validation."""
        with pytest.raises(ValueError, match="iterations must be positive"):
            PerformanceBenchmark(test_prompts=["test"], iterations=0)

        with pytest.raises(ValueError, match="concurrent_requests must be positive"):
            PerformanceBenchmark(test_prompts=["test"], concurrent_requests=0)

        with pytest.raises(ValueError, match="test_prompts cannot be empty"):
            PerformanceBenchmark(test_prompts=[])


class TestCostBenchmark:
    """Test cases for CostBenchmark."""

    @pytest.fixture
    def sample_prompts(self):
        """Sample test prompts."""
        return ["Write a short story", "Explain AI concepts", "Generate code"]

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.fixture
    def cost_benchmark(self, sample_prompts, mock_switch):
        """Create cost benchmark instance."""
        return CostBenchmark(
            test_prompts=sample_prompts, iterations=2, switch=mock_switch
        )

    @pytest.mark.asyncio
    async def test_cost_benchmark_initialization(self, cost_benchmark):
        """Test cost benchmark initialization."""
        assert cost_benchmark.test_prompts is not None
        assert len(cost_benchmark.test_prompts) == 3
        assert cost_benchmark.iterations == 2

    @pytest.mark.asyncio
    async def test_cost_benchmark_run_success(self, cost_benchmark, mock_switch):
        """Test successful cost benchmark run."""
        # Mock responses with different costs
        responses = [
            TaskResponse(
                content="Test response 1",
                provider="provider1",
                model_used="model1",
                tokens_used=100,
                cost=0.01,
                latency_ms=1000,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Test response 2",
                provider="provider2",
                model_used="model2",
                tokens_used=200,
                cost=0.02,
                latency_ms=1200,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = responses

        results = await cost_benchmark.run()

        assert results is not None
        assert results.avg_cost > 0
        assert results.total_cost > 0
        assert results.cost_per_token > 0
        assert len(results.provider_metrics) > 0

    @pytest.mark.asyncio
    async def test_cost_benchmark_cost_analysis(self, cost_benchmark, mock_switch):
        """Test cost analysis functionality."""
        # Mock responses with known costs
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=150,
            cost=0.015,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        results = await cost_benchmark.run()

        # Verify cost calculations
        expected_total_cost = (
            0.015 * len(cost_benchmark.test_prompts) * cost_benchmark.iterations
        )
        assert abs(results.total_cost - expected_total_cost) < 0.001

    @pytest.mark.asyncio
    async def test_cost_benchmark_provider_comparison(
        self, sample_prompts, mock_switch
    ):
        """Test cost comparison across providers."""
        benchmark = CostBenchmark(test_prompts=sample_prompts[:1], iterations=1)

        # Mock responses from different providers
        responses = [
            TaskResponse(
                content="Response from provider1",
                provider="provider1",
                model_used="model1",
                tokens_used=100,
                cost=0.01,
                latency_ms=1000,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Response from provider2",
                provider="provider2",
                model_used="model2",
                tokens_used=100,
                cost=0.02,
                latency_ms=1000,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = responses

        results = await benchmark.run()

        assert len(results.provider_metrics) == 2
        assert "provider1" in results.provider_metrics
        assert "provider2" in results.provider_metrics


class TestQualityBenchmark:
    """Test cases for QualityBenchmark."""

    @pytest.fixture
    def sample_test_cases(self):
        """Sample test cases for quality benchmark."""
        return [
            {
                "prompt": "What is the capital of France?",
                "expected": "Paris",
                "type": "factual",
            },
            {
                "prompt": "Write a haiku about nature",
                "expected": "5-7-5 syllable structure",
                "type": "creative",
            },
            {"prompt": "Solve: 2 + 2 = ?", "expected": "4", "type": "mathematical"},
        ]

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.fixture
    def quality_benchmark(self, sample_test_cases, mock_switch):
        """Create quality benchmark instance."""
        return QualityBenchmark(
            test_cases=sample_test_cases, iterations=2, switch=mock_switch
        )

    @pytest.mark.asyncio
    async def test_quality_benchmark_initialization(self, quality_benchmark):
        """Test quality benchmark initialization."""
        assert quality_benchmark.test_cases is not None
        assert len(quality_benchmark.test_cases) == 3
        assert quality_benchmark.iterations == 2

    @pytest.mark.asyncio
    async def test_quality_benchmark_run_success(self, quality_benchmark, mock_switch):
        """Test successful quality benchmark run."""
        # Mock responses
        responses = [
            TaskResponse(
                content="Paris",
                provider="test_provider",
                model_used="test_model",
                tokens_used=10,
                cost=0.001,
                latency_ms=500,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Cherry blossoms bloom\nGentle breeze through ancient trees\nNature's peaceful song",
                provider="test_provider",
                model_used="test_model",
                tokens_used=20,
                cost=0.002,
                latency_ms=800,
                finish_reason="stop",
            ),
            TaskResponse(
                content="4",
                provider="test_provider",
                model_used="test_model",
                tokens_used=5,
                cost=0.0005,
                latency_ms=300,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = responses

        results = await quality_benchmark.run()

        assert results is not None
        assert results.accuracy > 0
        assert results.quality_score > 0
        assert len(results.test_case_results) == 3

    @pytest.mark.asyncio
    async def test_quality_benchmark_accuracy_calculation(
        self, quality_benchmark, mock_switch
    ):
        """Test accuracy calculation."""
        # Mock perfect responses
        perfect_responses = [
            TaskResponse(
                content="Paris",
                provider="test",
                model_used="test",
                tokens_used=10,
                cost=0.001,
                latency_ms=500,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Perfect haiku",
                provider="test",
                model_used="test",
                tokens_used=20,
                cost=0.002,
                latency_ms=800,
                finish_reason="stop",
            ),
            TaskResponse(
                content="4",
                provider="test",
                model_used="test",
                tokens_used=5,
                cost=0.0005,
                latency_ms=300,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = perfect_responses

        results = await quality_benchmark.run()

        # Should have high accuracy for perfect responses
        assert results.accuracy > 0.8

    @pytest.mark.asyncio
    async def test_quality_benchmark_by_type(self, sample_test_cases, mock_switch):
        """Test quality benchmark results by type."""
        benchmark = QualityBenchmark(
            test_cases=sample_test_cases, iterations=1, switch=mock_switch
        )

        responses = [
            TaskResponse(
                content="Paris",
                provider="test",
                model_used="test",
                tokens_used=10,
                cost=0.001,
                latency_ms=500,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Good haiku",
                provider="test",
                model_used="test",
                tokens_used=20,
                cost=0.002,
                latency_ms=800,
                finish_reason="stop",
            ),
            TaskResponse(
                content="4",
                provider="test",
                model_used="test",
                tokens_used=5,
                cost=0.0005,
                latency_ms=300,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = responses

        results = await benchmark.run()

        assert "factual" in results.accuracy_by_type
        assert "creative" in results.accuracy_by_type
        assert "mathematical" in results.accuracy_by_type

    def test_quality_benchmark_validation(self):
        """Test quality benchmark input validation."""
        with pytest.raises(ValueError, match="test_cases cannot be empty"):
            QualityBenchmark(test_cases=[])

        with pytest.raises(ValueError, match="iterations must be positive"):
            QualityBenchmark(
                test_cases=[{"prompt": "test", "expected": "test", "type": "test"}],
                iterations=0,
            )


class TestCustomBenchmark:
    """Test cases for CustomBenchmark."""

    @pytest.fixture
    def custom_evaluator(self):
        """Custom evaluation function."""

        def evaluator(response: str, expected: str) -> float:
            # Simple similarity check
            if response.lower() == expected.lower():
                return 1.0
            elif expected.lower() in response.lower():
                return 0.8
            else:
                return 0.2

        return evaluator

    @pytest.fixture
    def sample_test_cases(self, custom_evaluator):
        """Sample test cases for custom benchmark."""
        return [
            {
                "prompt": "What is AI?",
                "expected": "Artificial Intelligence",
                "evaluator": custom_evaluator,
            },
            {
                "prompt": "Explain machine learning",
                "expected": "Machine learning is a subset of AI",
                "evaluator": custom_evaluator,
            },
        ]

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.fixture
    def custom_benchmark(self, sample_test_cases, mock_switch):
        """Create custom benchmark instance."""
        return CustomBenchmark(
            test_cases=sample_test_cases, iterations=2, switch=mock_switch
        )

    @pytest.mark.asyncio
    async def test_custom_benchmark_initialization(self, custom_benchmark):
        """Test custom benchmark initialization."""
        assert custom_benchmark.test_cases is not None
        assert len(custom_benchmark.test_cases) == 2
        assert custom_benchmark.iterations == 2

    @pytest.mark.asyncio
    async def test_custom_benchmark_run_success(self, custom_benchmark, mock_switch):
        """Test successful custom benchmark run."""
        responses = [
            TaskResponse(
                content="Artificial Intelligence is the simulation of human intelligence",
                provider="test_provider",
                model_used="test_model",
                tokens_used=20,
                cost=0.002,
                latency_ms=600,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Machine learning is a subset of AI that enables computers to learn",
                provider="test_provider",
                model_used="test_model",
                tokens_used=25,
                cost=0.0025,
                latency_ms=700,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = responses

        results = await custom_benchmark.run()

        assert results is not None
        assert results.custom_score > 0
        assert len(results.test_case_results) == 2

    @pytest.mark.asyncio
    async def test_custom_benchmark_evaluation(self, custom_benchmark, mock_switch):
        """Test custom evaluation function."""
        # Mock perfect response
        perfect_response = TaskResponse(
            content="Artificial Intelligence",
            provider="test_provider",
            model_used="test_model",
            tokens_used=10,
            cost=0.001,
            latency_ms=500,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = perfect_response

        results = await custom_benchmark.run()

        # Should have high score for perfect response
        assert results.custom_score > 0.8

    def test_custom_benchmark_validation(self):
        """Test custom benchmark input validation."""
        with pytest.raises(ValueError, match="test_cases cannot be empty"):
            CustomBenchmark(test_cases=[])

        with pytest.raises(ValueError, match="Each test case must have an evaluator"):
            CustomBenchmark(
                test_cases=[{"prompt": "test", "expected": "test"}]  # Missing evaluator
            )


class TestBenchmarkRunner:
    """Test cases for BenchmarkRunner."""

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.fixture
    def benchmark_runner(self, mock_switch):
        """Create benchmark runner instance."""
        return BenchmarkRunner(switch=mock_switch)

    @pytest.mark.asyncio
    async def test_benchmark_runner_initialization(self, benchmark_runner):
        """Test benchmark runner initialization."""
        assert benchmark_runner is not None

    @pytest.mark.asyncio
    async def test_run_performance_benchmark(self, benchmark_runner, mock_switch):
        """Test running performance benchmark."""
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        results = await benchmark_runner.run_performance_benchmark(
            providers=["test_provider"],
            models=["test_model"],
            test_prompts=["Test prompt"],
        )

        assert results is not None
        assert results.avg_latency > 0

    @pytest.mark.asyncio
    async def test_run_cost_benchmark(self, benchmark_runner, mock_switch):
        """Test running cost benchmark."""
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        results = await benchmark_runner.run_cost_benchmark(
            providers=["test_provider"],
            models=["test_model"],
            test_prompts=["Test prompt"],
        )

        assert results is not None
        assert results.avg_cost > 0

    @pytest.mark.asyncio
    async def test_run_quality_benchmark(self, benchmark_runner, mock_switch):
        """Test running quality benchmark."""
        mock_response = TaskResponse(
            content="Paris",
            provider="test_provider",
            model_used="test_model",
            tokens_used=10,
            cost=0.001,
            latency_ms=500,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        results = await benchmark_runner.run_quality_benchmark(
            providers=["test_provider"],
            models=["test_model"],
            test_cases=[
                {
                    "prompt": "What is the capital of France?",
                    "expected": "Paris",
                    "type": "factual",
                }
            ],
        )

        assert results is not None
        assert results.accuracy > 0

    @pytest.mark.asyncio
    async def test_run_comprehensive_benchmark(self, benchmark_runner, mock_switch):
        """Test running comprehensive benchmark."""
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        results = await benchmark_runner.run_comprehensive_benchmark(
            providers=["test_provider"],
            models=["test_model"],
            test_prompts=["Test prompt"],
            test_cases=[
                {
                    "prompt": "What is AI?",
                    "expected": "Artificial Intelligence",
                    "type": "factual",
                }
            ],
            iterations=1,
        )

        assert results is not None
        assert results.performance is not None
        assert results.cost is not None
        assert results.quality is not None


class TestBenchmarkAnalyzer:
    """Test cases for BenchmarkAnalyzer."""

    @pytest.fixture
    def sample_results(self):
        """Sample benchmark results for analysis."""
        # Mock comprehensive results
        results = MagicMock()
        results.performance = MagicMock()
        results.performance.avg_latency = 1000
        results.performance.min_latency = 800
        results.performance.max_latency = 1200
        results.performance.throughput = 60
        results.performance.success_rate = 0.95

        results.cost = MagicMock()
        results.cost.avg_cost = 0.01
        results.cost.total_cost = 1.0
        results.cost.cost_per_token = 0.0001

        results.quality = MagicMock()
        results.quality.accuracy = 0.9
        results.quality.quality_score = 8.5

        return results

    @pytest.fixture
    def benchmark_analyzer(self, sample_results):
        """Create benchmark analyzer instance."""
        return BenchmarkAnalyzer(sample_results)

    def test_benchmark_analyzer_initialization(self, benchmark_analyzer):
        """Test benchmark analyzer initialization."""
        assert benchmark_analyzer is not None

    def test_get_statistical_analysis(self, benchmark_analyzer):
        """Test statistical analysis."""
        stats = benchmark_analyzer.get_statistical_analysis()

        assert stats is not None
        assert hasattr(stats, "latency")
        assert hasattr(stats, "cost")
        assert hasattr(stats, "quality")

    def test_compare_providers(self, benchmark_analyzer):
        """Test provider comparison."""
        comparison = benchmark_analyzer.compare_providers()

        assert comparison is not None
        assert isinstance(comparison, dict)

    def test_get_trend_analysis(self, benchmark_analyzer):
        """Test trend analysis."""
        trends = benchmark_analyzer.get_trend_analysis()

        assert trends is not None
        assert isinstance(trends, dict)


class TestBenchmarkReporter:
    """Test cases for BenchmarkReporter."""

    @pytest.fixture
    def sample_results(self):
        """Sample benchmark results for reporting."""
        results = MagicMock()
        results.performance = MagicMock()
        results.cost = MagicMock()
        results.quality = MagicMock()
        return results

    @pytest.fixture
    def benchmark_reporter(self, sample_results):
        """Create benchmark reporter instance."""
        return BenchmarkReporter(sample_results)

    def test_benchmark_reporter_initialization(self, benchmark_reporter):
        """Test benchmark reporter initialization."""
        assert benchmark_reporter is not None

    def test_generate_html_report(self, benchmark_reporter, tmp_path):
        """Test HTML report generation."""
        output_file = tmp_path / "test_report.html"

        result = benchmark_reporter.generate_html_report(str(output_file))

        assert result is not None
        assert output_file.exists()

    def test_generate_json_report(self, benchmark_reporter, tmp_path):
        """Test JSON report generation."""
        output_file = tmp_path / "test_report.json"

        result = benchmark_reporter.generate_json_report(str(output_file))

        assert result is not None
        assert output_file.exists()

    def test_generate_csv_report(self, benchmark_reporter, tmp_path):
        """Test CSV report generation."""
        output_file = tmp_path / "test_report.csv"

        result = benchmark_reporter.generate_csv_report(str(output_file))

        assert result is not None
        assert output_file.exists()

    def test_generate_custom_report(self, benchmark_reporter, tmp_path):
        """Test custom report generation."""
        output_file = tmp_path / "test_custom_report.html"

        result = benchmark_reporter.generate_custom_report(
            template="basic_template", output_file=str(output_file), include_charts=True
        )

        assert result is not None
        assert output_file.exists()


class TestBenchmarkIntegration:
    """Integration tests for benchmark system."""

    @pytest.fixture
    def mock_switch(self):
        """Mock LLM switch for integration testing."""
        switch = MagicMock()
        switch.process_request = AsyncMock()
        return switch

    @pytest.mark.asyncio
    async def test_full_benchmark_workflow(self, mock_switch):
        """Test complete benchmark workflow."""
        # Mock responses
        mock_response = TaskResponse(
            content="Test response",
            provider="test_provider",
            model_used="test_model",
            tokens_used=100,
            cost=0.01,
            latency_ms=1000,
            finish_reason="stop",
        )
        mock_switch.process_request.return_value = mock_response

        # Create benchmark runner
        runner = BenchmarkRunner(switch=mock_switch)

        # Run comprehensive benchmark
        results = await runner.run_comprehensive_benchmark(
            providers=["test_provider"],
            models=["test_model"],
            test_prompts=["Test prompt"],
            test_cases=[
                {
                    "prompt": "What is AI?",
                    "expected": "Artificial Intelligence",
                    "type": "factual",
                }
            ],
            iterations=1,
        )

        # Analyze results
        analyzer = BenchmarkAnalyzer(results)
        stats = analyzer.get_statistical_analysis()
        comparison = analyzer.compare_providers()

        # Generate reports
        reporter = BenchmarkReporter(results)

        # Verify workflow completed successfully
        assert results is not None
        assert stats is not None
        assert comparison is not None
        assert reporter is not None

    @pytest.mark.asyncio
    async def test_benchmark_error_handling(self, mock_switch):
        """Test benchmark error handling."""
        # Mock failures
        mock_switch.process_request.side_effect = Exception("API Error")

        runner = BenchmarkRunner(switch=mock_switch)

        with pytest.raises(BenchmarkError):
            await runner.run_performance_benchmark(
                providers=["test_provider"],
                models=["test_model"],
                test_prompts=["Test prompt"],
            )

    @pytest.mark.asyncio
    async def test_benchmark_with_multiple_providers(self, mock_switch):
        """Test benchmark with multiple providers."""
        # Mock responses from different providers
        responses = [
            TaskResponse(
                content="Response from provider1",
                provider="provider1",
                model_used="model1",
                tokens_used=100,
                cost=0.01,
                latency_ms=1000,
                finish_reason="stop",
            ),
            TaskResponse(
                content="Response from provider2",
                provider="provider2",
                model_used="model2",
                tokens_used=120,
                cost=0.012,
                latency_ms=1200,
                finish_reason="stop",
            ),
        ]

        mock_switch.process_request.side_effect = responses

        runner = BenchmarkRunner(switch=mock_switch)

        results = await runner.run_performance_benchmark(
            providers=["provider1", "provider2"],
            models=["model1", "model2"],
            test_prompts=["Test prompt"],
        )

        assert results is not None
        assert len(results.provider_metrics) == 2


class TestBenchmarkUtilities:
    """Test cases for benchmark utility functions."""

    def test_benchmark_configuration_validation(self):
        """Test benchmark configuration validation."""
        from llm_dispatcher.benchmarks.utils import validate_benchmark_config

        # Valid configuration
        valid_config = {
            "iterations": 10,
            "concurrent_requests": 5,
            "timeout": 30000,
            "max_retries": 3,
        }

        assert validate_benchmark_config(valid_config) is True

        # Invalid configuration
        invalid_config = {
            "iterations": -1,  # Invalid
            "concurrent_requests": 0,  # Invalid
            "timeout": "invalid",  # Invalid type
        }

        with pytest.raises(ValueError):
            validate_benchmark_config(invalid_config)

    def test_benchmark_metrics_calculation(self):
        """Test benchmark metrics calculation."""
        from llm_dispatcher.benchmarks.utils import calculate_metrics

        # Sample data
        latencies = [1000, 1200, 800, 1500, 900]
        costs = [0.01, 0.012, 0.008, 0.015, 0.009]
        successes = [True, True, True, False, True]

        metrics = calculate_metrics(latencies, costs, successes)

        assert metrics["avg_latency"] > 0
        assert metrics["min_latency"] == 800
        assert metrics["max_latency"] == 1500
        assert metrics["success_rate"] == 0.8
        assert metrics["avg_cost"] > 0

    def test_benchmark_data_export(self):
        """Test benchmark data export functionality."""
        from llm_dispatcher.benchmarks.utils import export_benchmark_data

        # Sample benchmark data
        data = {
            "performance": {"avg_latency": 1000, "throughput": 60},
            "cost": {"avg_cost": 0.01, "total_cost": 1.0},
            "quality": {"accuracy": 0.9, "quality_score": 8.5},
        }

        # Test JSON export
        json_data = export_benchmark_data(data, format="json")
        assert json_data is not None
        assert isinstance(json_data, str)

        # Test CSV export
        csv_data = export_benchmark_data(data, format="csv")
        assert csv_data is not None
        assert isinstance(csv_data, str)


if __name__ == "__main__":
    pytest.main([__file__])
