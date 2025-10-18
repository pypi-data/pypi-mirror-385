"""
Custom benchmark implementations for LLM evaluation.

This module provides custom benchmarking tools for testing specific use cases
and scenarios with custom evaluation criteria.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import statistics
import json
from pathlib import Path

from ..core.base import LLMProvider, TaskRequest, TaskResponse, TaskType
from ..exceptions import BenchmarkError


@dataclass
class CustomResults:
    """Results from custom benchmark evaluation."""

    avg_score: float
    success_rate: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    provider_metrics: Dict[str, Dict[str, Any]]
    best_performer: str
    avg_latency: float
    custom_score: float  # Alias for avg_score
    test_case_results: List[Dict[str, Any]]  # Detailed results for each test case


@dataclass
class CustomTestCase:
    """A custom test case with specific evaluation criteria."""

    prompt: str
    expected_output: Optional[str] = None
    evaluator: Optional[Callable[[str, str], float]] = None
    context: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CustomMetrics:
    """Custom metrics for a single benchmark run."""

    total_score: float
    avg_score: float
    max_score: float
    min_score: float
    score_variance: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    avg_latency_ms: float


@dataclass
class CustomBenchmarkResult:
    """Result of a custom benchmark run."""

    provider: str
    model: str
    metrics: CustomMetrics
    timestamp: datetime
    test_cases: List[CustomTestCase]
    iterations: int
    detailed_results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class CustomBenchmark:
    """
    Custom benchmark for testing specific use cases and scenarios.

    This class provides flexible benchmarking capabilities for custom
    evaluation criteria and domain-specific testing scenarios.
    """

    def __init__(
        self,
        test_cases: List[CustomTestCase],
        iterations: int = 1,
        switch: Optional[LLMProvider] = None,
    ):
        """
        Initialize custom benchmark.

        Args:
            test_cases: List of custom test cases to evaluate
            iterations: Number of iterations to run for each test case
            switch: LLM switch instance to use for testing
        """
        if not test_cases:
            raise ValueError("test_cases cannot be empty")
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        # Convert dictionaries to CustomTestCase objects if needed
        converted_test_cases = []
        for i, test_case in enumerate(test_cases):
            if isinstance(test_case, dict):
                # Convert dictionary to CustomTestCase
                converted_test_case = CustomTestCase(
                    prompt=test_case.get("prompt", ""),
                    expected_output=test_case.get(
                        "expected", test_case.get("expected_output")
                    ),
                    evaluator=test_case.get("evaluator"),
                    context=test_case.get("context"),
                    metadata=test_case.get("metadata", {}),
                )
                converted_test_cases.append(converted_test_case)
            else:
                converted_test_cases.append(test_case)

        # Validate test cases
        for i, test_case in enumerate(converted_test_cases):
            if not test_case.prompt:
                raise ValueError(f"Test case {i} must have a prompt")
            if not test_case.evaluator and not test_case.expected_output:
                raise ValueError(
                    f"Test case {i} must have either an evaluator or expected output"
                )

        self.test_cases = converted_test_cases
        self.iterations = iterations
        self.switch = switch
        self.results: List[CustomBenchmarkResult] = []

    async def run_benchmark(
        self,
        providers: List[str],
        models: List[str],
        switch: Optional[LLMProvider] = None,
    ) -> List[CustomBenchmarkResult]:
        """
        Run custom benchmark across multiple providers and models.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            switch: LLM switch instance (overrides instance switch)

        Returns:
            List of custom benchmark results
        """
        if switch is None:
            switch = self.switch
        if switch is None:
            raise ValueError("No switch instance provided")

        results = []

        for provider in providers:
            for model in models:
                try:
                    result = await self._run_single_benchmark(provider, model, switch)
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = CustomBenchmarkResult(
                        provider=provider,
                        model=model,
                        metrics=CustomMetrics(
                            total_score=0.0,
                            avg_score=0.0,
                            max_score=0.0,
                            min_score=0.0,
                            score_variance=0.0,
                            total_tests=0,
                            passed_tests=0,
                            failed_tests=0,
                            success_rate=0.0,
                            avg_latency_ms=0.0,
                        ),
                        timestamp=datetime.now(),
                        test_cases=self.test_cases,
                        iterations=self.iterations,
                        errors=[str(e)],
                    )
                    results.append(error_result)

        self.results.extend(results)
        return results

    async def _run_single_benchmark(
        self, provider: str, model: str, switch: LLMProvider
    ) -> CustomBenchmarkResult:
        """Run custom benchmark for a single provider/model combination."""

        scores = []
        latencies = []
        detailed_results = []
        errors = []
        passed_tests = 0
        failed_tests = 0

        # Run each test case
        for test_case in self.test_cases:
            for iteration in range(self.iterations):
                try:
                    start_time = time.time()

                    # Create request
                    request = TaskRequest(
                        prompt=test_case.prompt,
                        task_type=TaskType.TEXT_GENERATION,
                        model=model,
                        provider=provider,
                        context=test_case.context,
                    )

                    # Get response
                    response = await switch.process_request(request)
                    end_time = time.time()

                    latency = (end_time - start_time) * 1000  # Convert to ms
                    latencies.append(latency)

                    if response and response.content:
                        # Evaluate the response
                        score = self._evaluate_response(test_case, response.content)
                        scores.append(score)

                        # Determine if test passed (score >= 0.7 is considered passing)
                        if score >= 0.7:
                            passed_tests += 1
                        else:
                            failed_tests += 1

                        detailed_results.append(
                            {
                                "test_case": (
                                    test_case.prompt[:100] + "..."
                                    if len(test_case.prompt) > 100
                                    else test_case.prompt
                                ),
                                "iteration": iteration,
                                "response": (
                                    response.content[:200] + "..."
                                    if len(response.content) > 200
                                    else response.content
                                ),
                                "score": score,
                                "latency_ms": latency,
                                "passed": score >= 0.7,
                            }
                        )
                    else:
                        failed_tests += 1
                        errors.append(
                            f"No response for test case: {test_case.prompt[:50]}..."
                        )

                except Exception as e:
                    failed_tests += 1
                    error_msg = f"Error in test case: {str(e)}"
                    errors.append(error_msg)
                    detailed_results.append(
                        {
                            "test_case": (
                                test_case.prompt[:100] + "..."
                                if len(test_case.prompt) > 100
                                else test_case.prompt
                            ),
                            "iteration": iteration,
                            "error": error_msg,
                            "score": 0.0,
                            "latency_ms": 0.0,
                            "passed": False,
                        }
                    )

        # Calculate metrics
        total_tests = passed_tests + failed_tests
        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0

        total_score = sum(scores) if scores else 0.0
        avg_score = statistics.mean(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0
        min_score = min(scores) if scores else 0.0
        score_variance = statistics.variance(scores) if len(scores) > 1 else 0.0
        avg_latency = statistics.mean(latencies) if latencies else 0.0

        metrics = CustomMetrics(
            total_score=total_score,
            avg_score=avg_score,
            max_score=max_score,
            min_score=min_score,
            score_variance=score_variance,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            avg_latency_ms=avg_latency,
        )

        return CustomBenchmarkResult(
            provider=provider,
            model=model,
            metrics=metrics,
            timestamp=datetime.now(),
            test_cases=self.test_cases,
            iterations=self.iterations,
            detailed_results=detailed_results,
            errors=errors,
        )

    def _evaluate_response(self, test_case: CustomTestCase, response: str) -> float:
        """
        Evaluate a response against the test case criteria.

        Args:
            test_case: The test case with evaluation criteria
            response: The response to evaluate

        Returns:
            Score between 0.0 and 1.0
        """
        if test_case.evaluator:
            # Use custom evaluator function
            try:
                return test_case.evaluator(test_case.expected_output or "", response)
            except Exception:
                return 0.0
        elif test_case.expected_output:
            # Use simple string similarity
            return self._calculate_similarity(test_case.expected_output, response)
        else:
            return 0.0

    def _calculate_similarity(self, expected: str, actual: str) -> float:
        """
        Calculate similarity between expected and actual responses.

        This is a simple implementation. In practice, you might want to use
        more sophisticated similarity measures like BLEU, ROUGE, or semantic similarity.
        """
        expected_lower = expected.lower().strip()
        actual_lower = actual.lower().strip()

        if expected_lower == actual_lower:
            return 1.0

        # Simple word overlap
        expected_words = set(expected_lower.split())
        actual_words = set(actual_lower.split())

        if not expected_words:
            return 0.0

        intersection = expected_words.intersection(actual_words)
        return len(intersection) / len(expected_words)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all custom benchmark results."""
        if not self.results:
            return {}

        all_scores = [r.metrics.avg_score for r in self.results]
        all_success_rates = [r.metrics.success_rate for r in self.results]
        all_latencies = [r.metrics.avg_latency_ms for r in self.results]

        return {
            "total_benchmarks": len(self.results),
            "avg_score": statistics.mean(all_scores),
            "max_score": max(all_scores),
            "min_score": min(all_scores),
            "avg_success_rate": statistics.mean(all_success_rates),
            "avg_latency_ms": statistics.mean(all_latencies),
            "best_performer": max(self.results, key=lambda r: r.metrics.avg_score),
            "fastest_performer": min(
                self.results, key=lambda r: r.metrics.avg_latency_ms
            ),
        }

    def save_results(self, filepath: Union[str, Path]) -> None:
        """Save custom benchmark results to a JSON file."""
        results_data = []
        for result in self.results:
            result_dict = {
                "provider": result.provider,
                "model": result.model,
                "timestamp": result.timestamp.isoformat(),
                "test_cases": [
                    {
                        "prompt": tc.prompt,
                        "expected_output": tc.expected_output,
                        "context": tc.context,
                        "metadata": tc.metadata,
                    }
                    for tc in result.test_cases
                ],
                "iterations": result.iterations,
                "metrics": {
                    "total_score": result.metrics.total_score,
                    "avg_score": result.metrics.avg_score,
                    "max_score": result.metrics.max_score,
                    "min_score": result.metrics.min_score,
                    "score_variance": result.metrics.score_variance,
                    "total_tests": result.metrics.total_tests,
                    "passed_tests": result.metrics.passed_tests,
                    "failed_tests": result.metrics.failed_tests,
                    "success_rate": result.metrics.success_rate,
                    "avg_latency_ms": result.metrics.avg_latency_ms,
                },
                "detailed_results": result.detailed_results,
                "errors": result.errors,
            }
            results_data.append(result_dict)

        with open(filepath, "w") as f:
            json.dump(results_data, f, indent=2)

    async def run(self) -> CustomResults:
        """
        Run the custom benchmark with default settings.

        Returns:
            Custom results summary
        """
        if not self.switch:
            raise ValueError("No switch instance provided")

        # Use default providers and models if not specified
        providers = ["test_provider"]
        models = ["test_model"]

        results = await self.run_benchmark(providers, models, self.switch)

        # Calculate summary metrics
        if not results:
            return CustomResults(
                avg_score=0.0,
                success_rate=0.0,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                provider_metrics={},
                best_performer="",
                avg_latency=0.0,
                custom_score=0.0,
                test_case_results=[],
            )

        # Calculate aggregate metrics
        all_scores = [r.metrics.avg_score for r in results]
        all_success_rates = [r.metrics.success_rate for r in results]
        all_latencies = [r.metrics.avg_latency_ms for r in results]

        avg_score = statistics.mean(all_scores) if all_scores else 0.0
        avg_success_rate = (
            statistics.mean(all_success_rates) if all_success_rates else 0.0
        )
        avg_latency = statistics.mean(all_latencies) if all_latencies else 0.0

        # Calculate totals
        total_tests = sum(r.metrics.total_tests for r in results)
        passed_tests = sum(r.metrics.passed_tests for r in results)
        failed_tests = sum(r.metrics.failed_tests for r in results)

        # Find best performer
        best_performer = (
            max(results, key=lambda r: r.metrics.avg_score).provider if results else ""
        )

        # Create provider metrics
        provider_metrics = {}
        for result in results:
            provider = result.provider
            if provider not in provider_metrics:
                provider_metrics[provider] = {}
            provider_metrics[provider] = {
                "avg_score": result.metrics.avg_score,
                "success_rate": result.metrics.success_rate,
                "total_tests": result.metrics.total_tests,
                "passed_tests": result.metrics.passed_tests,
                "failed_tests": result.metrics.failed_tests,
                "avg_latency_ms": result.metrics.avg_latency_ms,
            }

        # Create test case results (one per test case, not per iteration)
        test_case_results = []
        for result in results:
            # Group by test case and take the first result for each
            seen_test_cases = set()
            for detail in result.detailed_results:
                test_case = detail.get("test_case", "")
                if test_case not in seen_test_cases:
                    test_case_results.append(detail)
                    seen_test_cases.add(test_case)

        return CustomResults(
            avg_score=avg_score,
            success_rate=avg_success_rate,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            provider_metrics=provider_metrics,
            best_performer=best_performer,
            avg_latency=avg_latency,
            custom_score=avg_score,  # Alias for avg_score
            test_case_results=test_case_results,
        )
