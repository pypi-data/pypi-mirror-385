"""
Test fixtures and utilities for LLM-Dispatcher benchmarks.

This module contains shared fixtures, utilities, and helper functions
for benchmark testing.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock
from typing import List, Dict, Any, Optional

from llm_dispatcher.benchmarks import (
    PerformanceBenchmark,
    CostBenchmark,
    QualityBenchmark,
    CustomBenchmark,
    BenchmarkRunner,
)
from llm_dispatcher.core.base import TaskRequest, TaskResponse, TaskType
from llm_dispatcher import LLMSwitch


class BenchmarkTestFixtures:
    """Shared fixtures for benchmark testing."""

    @staticmethod
    @pytest.fixture
    def sample_prompts():
        """Sample prompts for testing."""
        return [
            "Write a short story about a robot learning to paint",
            "Explain the concept of machine learning in simple terms",
            "Generate Python code to implement a binary search algorithm",
            "Create a marketing slogan for a new AI product",
            "Summarize the key benefits of renewable energy",
            "Write a haiku about artificial intelligence",
            "Explain quantum computing to a 10-year-old",
            "Generate a recipe for chocolate chip cookies",
            "Describe the process of photosynthesis",
            "Write a limerick about programming",
        ]

    @staticmethod
    @pytest.fixture
    def sample_test_cases():
        """Sample test cases for quality benchmarks."""
        return [
            {
                "prompt": "What is the capital of France?",
                "expected": "Paris",
                "type": "factual",
            },
            {
                "prompt": "Write a haiku about spring",
                "expected": "5-7-5 syllable structure",
                "type": "creative",
            },
            {
                "prompt": "Solve: 15 * 23 = ?",
                "expected": "345",
                "type": "mathematical",
            },
            {
                "prompt": "What is the largest planet in our solar system?",
                "expected": "Jupiter",
                "type": "factual",
            },
            {
                "prompt": "Write a limerick about cats",
                "expected": "AABBA rhyme scheme",
                "type": "creative",
            },
        ]

    @staticmethod
    @pytest.fixture
    def mock_providers_config():
        """Mock provider configuration."""
        return {
            "openai": {
                "api_key": "sk-test-openai-key",
                "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            },
            "anthropic": {
                "api_key": "sk-ant-test-anthropic-key",
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            },
            "google": {
                "api_key": "test-google-key",
                "models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro"],
            },
            "grok": {
                "api_key": "test-grok-key",
                "models": ["grok-beta", "grok-2"],
            },
        }

    @staticmethod
    @pytest.fixture
    def mock_llm_switch(mock_providers_config):
        """Create mock LLM switch for testing."""
        switch = MagicMock(spec=LLMSwitch)
        switch.providers = mock_providers_config
        switch.process_request = AsyncMock()
        switch.get_available_providers = MagicMock(
            return_value=list(mock_providers_config.keys())
        )
        switch.get_provider_status = MagicMock(
            return_value={
                provider: "healthy" for provider in mock_providers_config.keys()
            }
        )
        return switch

    @staticmethod
    @pytest.fixture
    def mock_task_response():
        """Create mock task response."""
        return TaskResponse(
            content="Mock response content",
            provider="mock_provider",
            model="mock_model",
            tokens_used=100,
            cost=0.01,
            latency=1000,
        )

    @staticmethod
    @pytest.fixture
    def mock_task_request():
        """Create mock task request."""
        return TaskRequest(
            prompt="Mock test prompt",
            task_type=TaskType.TEXT_GENERATION,
            max_tokens=100,
            temperature=0.7,
        )

    @staticmethod
    @pytest.fixture
    def custom_evaluator():
        """Custom evaluation function for testing."""

        def evaluator(response: str, expected: str) -> float:
            """Simple similarity-based evaluator."""
            response_lower = response.lower()
            expected_lower = expected.lower()

            if expected_lower in response_lower:
                return 1.0
            elif any(word in response_lower for word in expected_lower.split()):
                return 0.7
            else:
                return 0.2

        return evaluator

    @staticmethod
    @pytest.fixture
    def benchmark_config():
        """Standard benchmark configuration."""
        return {
            "iterations": 3,
            "concurrent_requests": 5,
            "timeout": 30000,
            "max_retries": 3,
            "warmup_requests": 1,
            "cooldown_time": 1000,
        }

    @staticmethod
    @pytest.fixture
    def performance_benchmark(sample_prompts, mock_llm_switch, benchmark_config):
        """Create performance benchmark instance."""
        return PerformanceBenchmark(
            test_prompts=sample_prompts,
            iterations=benchmark_config["iterations"],
            concurrent_requests=benchmark_config["concurrent_requests"],
            switch=mock_llm_switch,
        )

    @staticmethod
    @pytest.fixture
    def cost_benchmark(sample_prompts, mock_llm_switch, benchmark_config):
        """Create cost benchmark instance."""
        return CostBenchmark(
            test_prompts=sample_prompts,
            iterations=benchmark_config["iterations"],
            switch=mock_llm_switch,
        )

    @staticmethod
    @pytest.fixture
    def quality_benchmark(sample_test_cases, mock_llm_switch, benchmark_config):
        """Create quality benchmark instance."""
        return QualityBenchmark(
            test_cases=sample_test_cases,
            iterations=benchmark_config["iterations"],
            switch=mock_llm_switch,
        )

    @staticmethod
    @pytest.fixture
    def custom_benchmark(custom_evaluator, mock_llm_switch, benchmark_config):
        """Create custom benchmark instance."""
        test_cases = [
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
        ]

        return CustomBenchmark(
            test_cases=test_cases,
            iterations=benchmark_config["iterations"],
            switch=mock_llm_switch,
        )

    @staticmethod
    @pytest.fixture
    def benchmark_runner(mock_llm_switch):
        """Create benchmark runner instance."""
        return BenchmarkRunner(switch=mock_llm_switch)


class BenchmarkTestHelpers:
    """Helper functions for benchmark testing."""

    @staticmethod
    def create_mock_responses(
        count: int, provider: str = "test_provider"
    ) -> List[TaskResponse]:
        """Create a list of mock responses."""
        responses = []
        for i in range(count):
            responses.append(
                TaskResponse(
                    content=f"Mock response {i}",
                    provider=provider,
                    model=f"test_model_{i % 3}",
                    tokens_used=100 + i * 10,
                    cost=0.01 + i * 0.001,
                    latency=1000 + i * 100,
                )
            )
        return responses

    @staticmethod
    def create_mock_responses_with_failures(
        count: int, failure_rate: float = 0.1
    ) -> List[Any]:
        """Create mock responses with some failures."""
        responses = []
        failure_count = int(count * failure_rate)

        for i in range(count):
            if i < failure_count:
                # Create failure
                responses.append(Exception(f"Mock failure {i}"))
            else:
                responses.append(
                    TaskResponse(
                        content=f"Mock response {i}",
                        provider="test_provider",
                        model="test_model",
                        tokens_used=100,
                        cost=0.01,
                        latency=1000,
                    )
                )
        return responses

    @staticmethod
    def create_large_prompt_set(size: int) -> List[str]:
        """Create a large set of test prompts."""
        return [f"Large prompt set item {i}" for i in range(size)]

    @staticmethod
    def create_large_test_cases(size: int) -> List[Dict[str, Any]]:
        """Create a large set of test cases."""
        return [
            {
                "prompt": f"Test case {i}: What is the answer to question {i}?",
                "expected": f"Answer {i}",
                "type": "factual",
            }
            for i in range(size)
        ]

    @staticmethod
    def create_benchmark_config(
        iterations: int = 3,
        concurrent_requests: int = 5,
        timeout: int = 30000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create benchmark configuration."""
        config = {
            "iterations": iterations,
            "concurrent_requests": concurrent_requests,
            "timeout": timeout,
            "max_retries": 3,
            "warmup_requests": 1,
            "cooldown_time": 1000,
        }
        config.update(kwargs)
        return config

    @staticmethod
    async def run_benchmark_with_timeout(benchmark, timeout: int = 30) -> Any:
        """Run benchmark with timeout."""
        try:
            return await asyncio.wait_for(benchmark.run(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Benchmark timed out after {timeout} seconds")

    @staticmethod
    def assert_benchmark_results_valid(results) -> None:
        """Assert that benchmark results are valid."""
        assert results is not None
        assert hasattr(results, "success_rate")
        assert hasattr(results, "total_requests")
        assert 0 <= results.success_rate <= 1
        assert results.total_requests > 0

    @staticmethod
    def assert_performance_results_valid(results) -> None:
        """Assert that performance benchmark results are valid."""
        BenchmarkTestHelpers.assert_benchmark_results_valid(results)
        assert hasattr(results, "avg_latency")
        assert hasattr(results, "throughput")
        assert results.avg_latency > 0
        assert results.throughput > 0

    @staticmethod
    def assert_cost_results_valid(results) -> None:
        """Assert that cost benchmark results are valid."""
        BenchmarkTestHelpers.assert_benchmark_results_valid(results)
        assert hasattr(results, "avg_cost")
        assert hasattr(results, "total_cost")
        assert results.avg_cost >= 0
        assert results.total_cost >= 0

    @staticmethod
    def assert_quality_results_valid(results) -> None:
        """Assert that quality benchmark results are valid."""
        BenchmarkTestHelpers.assert_benchmark_results_valid(results)
        assert hasattr(results, "accuracy")
        assert hasattr(results, "quality_score")
        assert 0 <= results.accuracy <= 1
        assert results.quality_score >= 0

    @staticmethod
    def create_temp_config_file(config: Dict[str, Any]) -> str:
        """Create temporary configuration file."""
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            return f.name

    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Clean up temporary file."""
        if os.path.exists(file_path):
            os.unlink(file_path)


class BenchmarkTestData:
    """Test data for benchmarks."""

    # Sample prompts for different use cases
    CREATIVE_PROMPTS = [
        "Write a short story about a time-traveling detective",
        "Create a poem about the beauty of mathematics",
        "Design a fantasy world with unique magic system",
        "Write a comedy sketch about AI assistants",
        "Create a song about the future of technology",
    ]

    TECHNICAL_PROMPTS = [
        "Explain the concept of recursion in programming",
        "Describe the TCP/IP protocol stack",
        "How does a neural network learn?",
        "What is the difference between SQL and NoSQL databases?",
        "Explain the CAP theorem in distributed systems",
    ]

    BUSINESS_PROMPTS = [
        "Write a business plan for a sustainable energy startup",
        "Create a marketing strategy for a new mobile app",
        "Analyze the competitive landscape for electric vehicles",
        "Write a proposal for implementing AI in healthcare",
        "Create a financial forecast for a SaaS company",
    ]

    # Test cases for quality benchmarks
    FACTUAL_TEST_CASES = [
        {
            "prompt": "What is the capital of Australia?",
            "expected": "Canberra",
            "type": "factual",
        },
        {
            "prompt": "Who wrote 'To Kill a Mockingbird'?",
            "expected": "Harper Lee",
            "type": "factual",
        },
        {
            "prompt": "What is the chemical symbol for gold?",
            "expected": "Au",
            "type": "factual",
        },
    ]

    CREATIVE_TEST_CASES = [
        {
            "prompt": "Write a haiku about winter",
            "expected": "5-7-5 syllable structure",
            "type": "creative",
        },
        {
            "prompt": "Create a limerick about a programmer",
            "expected": "AABBA rhyme scheme",
            "type": "creative",
        },
        {
            "prompt": "Write a short story opening",
            "expected": "engaging narrative beginning",
            "type": "creative",
        },
    ]

    MATHEMATICAL_TEST_CASES = [
        {
            "prompt": "What is 127 * 83?",
            "expected": "10541",
            "type": "mathematical",
        },
        {
            "prompt": "Solve: 2x + 5 = 17",
            "expected": "x = 6",
            "type": "mathematical",
        },
        {
            "prompt": "What is the square root of 144?",
            "expected": "12",
            "type": "mathematical",
        },
    ]

    # Provider-specific test data
    PROVIDER_TEST_DATA = {
        "openai": {
            "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "strengths": ["code generation", "creative writing", "analysis"],
            "cost_range": (0.01, 0.06),
            "latency_range": (800, 2000),
        },
        "anthropic": {
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "strengths": ["reasoning", "analysis", "safety"],
            "cost_range": (0.015, 0.075),
            "latency_range": (1000, 2500),
        },
        "google": {
            "models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro"],
            "strengths": ["multimodal", "reasoning", "efficiency"],
            "cost_range": (0.005, 0.035),
            "latency_range": (600, 1800),
        },
        "grok": {
            "models": ["grok-beta", "grok-2"],
            "strengths": ["humor", "creativity", "real-time"],
            "cost_range": (0.01, 0.04),
            "latency_range": (500, 1500),
        },
    }


# Export fixtures for use in other test modules
sample_prompts = BenchmarkTestFixtures.sample_prompts
sample_test_cases = BenchmarkTestFixtures.sample_test_cases
mock_providers_config = BenchmarkTestFixtures.mock_providers_config
mock_llm_switch = BenchmarkTestFixtures.mock_llm_switch
mock_task_response = BenchmarkTestFixtures.mock_task_response
mock_task_request = BenchmarkTestFixtures.mock_task_request
custom_evaluator = BenchmarkTestFixtures.custom_evaluator
benchmark_config = BenchmarkTestFixtures.benchmark_config
performance_benchmark = BenchmarkTestFixtures.performance_benchmark
cost_benchmark = BenchmarkTestFixtures.cost_benchmark
quality_benchmark = BenchmarkTestFixtures.quality_benchmark
custom_benchmark = BenchmarkTestFixtures.custom_benchmark
benchmark_runner = BenchmarkTestFixtures.benchmark_runner


if __name__ == "__main__":
    # Run basic tests on fixtures
    pytest.main([__file__])
