"""
Benchmark runner for orchestrating comprehensive LLM evaluations.

This module provides a unified interface for running multiple types of benchmarks
and coordinating comprehensive evaluation workflows.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from ..core.base import LLMProvider, TaskRequest, TaskResponse, TaskType
from ..exceptions import BenchmarkError
from .performance_benchmark import PerformanceBenchmark, BenchmarkResult
from .cost_benchmark import CostBenchmark, CostBenchmarkResult
from .quality_benchmark import QualityBenchmark
from .custom_benchmark import CustomBenchmark, CustomBenchmarkResult


@dataclass
class ComprehensiveBenchmarkResult:
    """Result of a comprehensive benchmark run."""

    performance_results: List[BenchmarkResult] = field(default_factory=list)
    cost_results: List[CostBenchmarkResult] = field(default_factory=list)
    quality_results: List[Any] = field(default_factory=list)  # QualityBenchmarkResult
    custom_results: List[CustomBenchmarkResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    total_duration: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def performance(self):
        """Alias for performance_results for backward compatibility."""
        return self.performance_results

    @property
    def cost(self):
        """Alias for cost_results for backward compatibility."""
        return self.cost_results

    @property
    def quality(self):
        """Alias for quality_results for backward compatibility."""
        return self.quality_results


class BenchmarkRunner:
    """
    Comprehensive benchmark runner for orchestrating multiple benchmark types.

    This class provides a unified interface for running performance, cost, quality,
    and custom benchmarks across multiple providers and models.
    """

    def __init__(self, switch: Optional[LLMProvider] = None):
        """
        Initialize benchmark runner.

        Args:
            switch: LLM switch instance to use for testing
        """
        self.switch = switch
        self.results: List[ComprehensiveBenchmarkResult] = []

    async def run_performance_benchmark(
        self,
        providers: List[str],
        models: List[str],
        test_prompts: List[str],
        iterations: int = 1,
        concurrent_requests: int = 1,
        timeout: float = 30.0,
    ) -> Any:  # PerformanceResults
        """
        Run performance benchmark.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            test_prompts: List of test prompts
            iterations: Number of iterations per prompt
            concurrent_requests: Number of concurrent requests
            timeout: Request timeout in seconds

        Returns:
            PerformanceResults object with aggregated metrics
        """
        benchmark = PerformanceBenchmark(
            test_prompts=test_prompts,
            iterations=iterations,
            concurrent_requests=concurrent_requests,
            timeout=timeout,
            switch=self.switch,
        )

        return await benchmark.run()

    async def run_cost_benchmark(
        self,
        providers: List[str],
        models: List[str],
        test_prompts: List[str],
        iterations: int = 1,
    ) -> Any:  # CostResults
        """
        Run cost benchmark.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            test_prompts: List of test prompts
            iterations: Number of iterations per prompt

        Returns:
            CostResults object with aggregated metrics
        """
        benchmark = CostBenchmark(
            test_prompts=test_prompts, iterations=iterations, switch=self.switch
        )

        return await benchmark.run()

    async def run_quality_benchmark(
        self,
        providers: List[str],
        models: List[str],
        test_cases: List[Any],  # QualityBenchmark test cases
        iterations: int = 1,
    ) -> Any:  # QualityResults
        """
        Run quality benchmark.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            test_cases: List of quality test cases
            iterations: Number of iterations per test case

        Returns:
            QualityResults object with aggregated metrics
        """
        benchmark = QualityBenchmark(
            test_cases=test_cases, iterations=iterations, switch=self.switch
        )

        return await benchmark.run()

    async def run_custom_benchmark(
        self,
        providers: List[str],
        models: List[str],
        test_cases: List[Any],  # CustomBenchmark test cases
        iterations: int = 1,
    ) -> Any:  # CustomResults
        """
        Run custom benchmark.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            test_cases: List of custom test cases
            iterations: Number of iterations per test case

        Returns:
            CustomResults object with aggregated metrics
        """
        benchmark = CustomBenchmark(
            test_cases=test_cases, iterations=iterations, switch=self.switch
        )

        return await benchmark.run()

    async def run_comprehensive_benchmark(
        self,
        providers: List[str],
        models: List[str],
        test_prompts: List[str],
        test_cases: Optional[List[Any]] = None,
        custom_test_cases: Optional[List[Any]] = None,
        iterations: int = 1,
        concurrent_requests: int = 1,
        timeout: float = 30.0,
        include_performance: bool = True,
        include_cost: bool = True,
        include_quality: bool = False,
        include_custom: bool = False,
    ) -> ComprehensiveBenchmarkResult:
        """
        Run comprehensive benchmark including multiple benchmark types.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            test_prompts: List of test prompts for performance/cost benchmarks
            test_cases: List of quality test cases
            custom_test_cases: List of custom test cases
            iterations: Number of iterations per test
            concurrent_requests: Number of concurrent requests for performance tests
            timeout: Request timeout in seconds
            include_performance: Whether to include performance benchmark
            include_cost: Whether to include cost benchmark
            include_quality: Whether to include quality benchmark
            include_custom: Whether to include custom benchmark

        Returns:
            Comprehensive benchmark result
        """
        start_time = time.time()
        errors = []

        result = ComprehensiveBenchmarkResult()

        # Run performance benchmark
        if include_performance:
            try:
                result.performance_results = await self.run_performance_benchmark(
                    providers=providers,
                    models=models,
                    test_prompts=test_prompts,
                    iterations=iterations,
                    concurrent_requests=concurrent_requests,
                    timeout=timeout,
                )
            except Exception as e:
                error_msg = f"Performance benchmark failed: {str(e)}"
                errors.append(error_msg)

        # Run cost benchmark
        if include_cost:
            try:
                result.cost_results = await self.run_cost_benchmark(
                    providers=providers,
                    models=models,
                    test_prompts=test_prompts,
                    iterations=iterations,
                )
            except Exception as e:
                error_msg = f"Cost benchmark failed: {str(e)}"
                errors.append(error_msg)

        # Run quality benchmark
        if include_quality and test_cases:
            try:
                result.quality_results = await self.run_quality_benchmark(
                    providers=providers,
                    models=models,
                    test_cases=test_cases,
                    iterations=iterations,
                )
            except Exception as e:
                error_msg = f"Quality benchmark failed: {str(e)}"
                errors.append(error_msg)

        # Run custom benchmark
        if include_custom and custom_test_cases:
            try:
                result.custom_results = await self.run_custom_benchmark(
                    providers=providers,
                    models=models,
                    test_cases=custom_test_cases,
                    iterations=iterations,
                )
            except Exception as e:
                error_msg = f"Custom benchmark failed: {str(e)}"
                errors.append(error_msg)

        # Calculate total duration
        end_time = time.time()
        result.total_duration = end_time - start_time
        result.errors = errors

        self.results.append(result)
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all benchmark results."""
        if not self.results:
            return {}

        total_benchmarks = len(self.results)
        total_duration = sum(r.total_duration for r in self.results)

        # Aggregate results by type
        all_performance = []
        all_cost = []
        all_quality = []
        all_custom = []

        for result in self.results:
            all_performance.extend(result.performance_results)
            all_cost.extend(result.cost_results)
            all_quality.extend(result.quality_results)
            all_custom.extend(result.custom_results)

        summary = {
            "total_comprehensive_benchmarks": total_benchmarks,
            "total_duration_seconds": total_duration,
            "avg_duration_per_benchmark": (
                total_duration / total_benchmarks if total_benchmarks > 0 else 0
            ),
            "performance_benchmarks": len(all_performance),
            "cost_benchmarks": len(all_cost),
            "quality_benchmarks": len(all_quality),
            "custom_benchmarks": len(all_custom),
            "total_errors": sum(len(r.errors) for r in self.results),
        }

        # Add performance summary if available
        if all_performance:
            latencies = [r.metrics.latency_ms for r in all_performance]
            success_rates = [r.metrics.success_rate for r in all_performance]
            summary["performance_summary"] = {
                "avg_latency_ms": sum(latencies) / len(latencies),
                "avg_success_rate": sum(success_rates) / len(success_rates),
                "best_performer": max(
                    all_performance, key=lambda r: r.metrics.success_rate
                ),
                "fastest_performer": min(
                    all_performance, key=lambda r: r.metrics.latency_ms
                ),
            }

        # Add cost summary if available
        if all_cost:
            costs = [r.metrics.total_cost for r in all_cost]
            tokens_per_dollar = [r.metrics.tokens_per_dollar for r in all_cost]
            summary["cost_summary"] = {
                "avg_total_cost": sum(costs) / len(costs),
                "avg_tokens_per_dollar": sum(tokens_per_dollar)
                / len(tokens_per_dollar),
                "most_cost_effective": max(
                    all_cost, key=lambda r: r.metrics.tokens_per_dollar
                ),
                "least_cost_effective": min(
                    all_cost, key=lambda r: r.metrics.tokens_per_dollar
                ),
            }

        return summary

    def save_results(self, filepath: Union[str, Path]) -> None:
        """Save all benchmark results to a JSON file."""
        results_data = []
        for result in self.results:
            result_dict = {
                "timestamp": result.timestamp.isoformat(),
                "total_duration": result.total_duration,
                "errors": result.errors,
                "performance_results": [
                    {
                        "provider": r.provider,
                        "model": r.model,
                        "metrics": {
                            "latency_ms": r.metrics.latency_ms,
                            "tokens_per_second": r.metrics.tokens_per_second,
                            "requests_per_second": r.metrics.requests_per_second,
                            "success_rate": r.metrics.success_rate,
                            "error_count": r.metrics.error_count,
                            "total_requests": r.metrics.total_requests,
                            "total_tokens": r.metrics.total_tokens,
                            "avg_response_length": r.metrics.avg_response_length,
                        },
                        "errors": r.errors,
                    }
                    for r in result.performance_results
                ],
                "cost_results": [
                    {
                        "provider": r.provider,
                        "model": r.model,
                        "metrics": {
                            "total_cost": r.metrics.total_cost,
                            "cost_per_token": r.metrics.cost_per_token,
                            "cost_per_request": r.metrics.cost_per_request,
                            "tokens_per_dollar": r.metrics.tokens_per_dollar,
                            "requests_per_dollar": r.metrics.requests_per_dollar,
                            "total_tokens": r.metrics.total_tokens,
                            "total_requests": r.metrics.total_requests,
                            "avg_tokens_per_request": r.metrics.avg_tokens_per_request,
                        },
                        "errors": r.errors,
                    }
                    for r in result.cost_results
                ],
                "custom_results": [
                    {
                        "provider": r.provider,
                        "model": r.model,
                        "metrics": {
                            "total_score": r.metrics.total_score,
                            "avg_score": r.metrics.avg_score,
                            "max_score": r.metrics.max_score,
                            "min_score": r.metrics.min_score,
                            "score_variance": r.metrics.score_variance,
                            "total_tests": r.metrics.total_tests,
                            "passed_tests": r.metrics.passed_tests,
                            "failed_tests": r.metrics.failed_tests,
                            "success_rate": r.metrics.success_rate,
                            "avg_latency_ms": r.metrics.avg_latency_ms,
                        },
                        "errors": r.errors,
                    }
                    for r in result.custom_results
                ],
            }
            results_data.append(result_dict)

        with open(filepath, "w") as f:
            json.dump(results_data, f, indent=2)
