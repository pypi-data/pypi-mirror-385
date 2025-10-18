"""
Performance benchmark implementations for LLM evaluation.

This module provides performance benchmarking tools for measuring latency,
throughput, and other performance metrics across different LLM providers.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import statistics
import json
from pathlib import Path

from ..core.base import LLMProvider, TaskRequest, TaskResponse, TaskType
from ..exceptions import BenchmarkError


@dataclass
class PerformanceResults:
    """Results from performance benchmark evaluation."""

    avg_latency: float
    throughput: float
    success_rate: float
    provider_metrics: Dict[str, Dict[str, Any]]
    total_requests: int
    total_errors: int
    avg_tokens_per_second: float


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single benchmark run."""

    latency_ms: float
    tokens_per_second: float
    requests_per_second: float
    success_rate: float
    error_count: int
    total_requests: int
    total_tokens: int
    avg_response_length: int


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark run."""

    provider: str
    model: str
    metrics: PerformanceMetrics
    timestamp: datetime
    test_prompts: List[str]
    iterations: int
    concurrent_requests: int
    errors: List[str] = field(default_factory=list)


class PerformanceBenchmark:
    """
    Performance benchmark for measuring LLM response times and throughput.

    This class provides comprehensive performance testing capabilities including
    latency measurement, throughput analysis, and concurrent request handling.
    """

    def __init__(
        self,
        test_prompts: List[str],
        iterations: int = 1,
        concurrent_requests: int = 1,
        timeout: float = 30.0,
        switch: Optional[LLMProvider] = None,
    ):
        """
        Initialize performance benchmark.

        Args:
            test_prompts: List of test prompts to use for benchmarking
            iterations: Number of iterations to run for each prompt
            concurrent_requests: Number of concurrent requests to make
            timeout: Timeout for individual requests in seconds
            switch: LLM switch instance to use for testing
        """
        if not test_prompts:
            raise ValueError("test_prompts cannot be empty")
        if iterations <= 0:
            raise ValueError("iterations must be positive")
        if concurrent_requests <= 0:
            raise ValueError("concurrent_requests must be positive")

        self.test_prompts = test_prompts
        self.iterations = iterations
        self.concurrent_requests = concurrent_requests
        self.timeout = timeout
        self.switch = switch
        self.results: List[BenchmarkResult] = []

    async def run_benchmark(
        self,
        providers: List[str],
        models: List[str],
        switch: Optional[LLMProvider] = None,
    ) -> List[BenchmarkResult]:
        """
        Run performance benchmark across multiple providers and models.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            switch: LLM switch instance (overrides instance switch)

        Returns:
            List of benchmark results
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
                    error_result = BenchmarkResult(
                        provider=provider,
                        model=model,
                        metrics=PerformanceMetrics(
                            latency_ms=0.0,
                            tokens_per_second=0.0,
                            requests_per_second=0.0,
                            success_rate=0.0,
                            error_count=1,
                            total_requests=0,
                            total_tokens=0,
                            avg_response_length=0,
                        ),
                        timestamp=datetime.now(),
                        test_prompts=self.test_prompts,
                        iterations=self.iterations,
                        concurrent_requests=self.concurrent_requests,
                        errors=[str(e)],
                    )
                    results.append(error_result)

        self.results.extend(results)
        return results

    async def _run_single_benchmark(
        self, provider: str, model: str, switch: LLMProvider
    ) -> BenchmarkResult:
        """Run benchmark for a single provider/model combination."""

        latencies = []
        token_counts = []
        response_lengths = []
        errors = []
        total_requests = 0

        # Create all requests
        all_requests = []
        for prompt in self.test_prompts:
            for _ in range(self.iterations):
                request = TaskRequest(
                    prompt=prompt,
                    task_type=TaskType.TEXT_GENERATION,
                    model=model,
                    provider=provider,
                )
                all_requests.append(request)

        total_requests = len(all_requests)

        # Run requests with concurrency control
        semaphore = asyncio.Semaphore(self.concurrent_requests)

        async def process_request(request: TaskRequest) -> Optional[float]:
            async with semaphore:
                try:
                    start_time = time.time()
                    response = await asyncio.wait_for(
                        switch.process_request(request), timeout=self.timeout
                    )
                    end_time = time.time()

                    latency = (end_time - start_time) * 1000  # Convert to ms
                    latencies.append(latency)

                    if response and response.content:
                        token_counts.append(len(response.content.split()))
                        response_lengths.append(len(response.content))

                    return latency

                except asyncio.TimeoutError:
                    errors.append(f"Timeout for request: {request.prompt[:50]}...")
                    return None
                except Exception as e:
                    errors.append(f"Error for request: {str(e)}")
                    return None

        # Execute all requests
        await asyncio.gather(*[process_request(req) for req in all_requests])

        # Calculate metrics
        success_count = len(latencies)
        success_rate = success_count / total_requests if total_requests > 0 else 0.0

        avg_latency = statistics.mean(latencies) if latencies else 0.0
        total_tokens = sum(token_counts) if token_counts else 0
        avg_response_length = (
            statistics.mean(response_lengths) if response_lengths else 0
        )

        # Calculate throughput metrics
        total_time = sum(latencies) / 1000.0 if latencies else 1.0  # Convert to seconds
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0.0
        requests_per_second = success_count / total_time if total_time > 0 else 0.0

        metrics = PerformanceMetrics(
            latency_ms=avg_latency,
            tokens_per_second=tokens_per_second,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            error_count=len(errors),
            total_requests=total_requests,
            total_tokens=total_tokens,
            avg_response_length=int(avg_response_length),
        )

        return BenchmarkResult(
            provider=provider,
            model=model,
            metrics=metrics,
            timestamp=datetime.now(),
            test_prompts=self.test_prompts,
            iterations=self.iterations,
            concurrent_requests=self.concurrent_requests,
            errors=errors,
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all benchmark results."""
        if not self.results:
            return {}

        all_latencies = [r.metrics.latency_ms for r in self.results]
        all_success_rates = [r.metrics.success_rate for r in self.results]
        all_tokens_per_second = [r.metrics.tokens_per_second for r in self.results]

        return {
            "total_benchmarks": len(self.results),
            "avg_latency_ms": statistics.mean(all_latencies),
            "min_latency_ms": min(all_latencies),
            "max_latency_ms": max(all_latencies),
            "avg_success_rate": statistics.mean(all_success_rates),
            "avg_tokens_per_second": statistics.mean(all_tokens_per_second),
            "best_performer": max(self.results, key=lambda r: r.metrics.success_rate),
            "fastest_performer": min(self.results, key=lambda r: r.metrics.latency_ms),
        }

    def save_results(self, filepath: Union[str, Path]) -> None:
        """Save benchmark results to a JSON file."""
        results_data = []
        for result in self.results:
            result_dict = {
                "provider": result.provider,
                "model": result.model,
                "timestamp": result.timestamp.isoformat(),
                "test_prompts": result.test_prompts,
                "iterations": result.iterations,
                "concurrent_requests": result.concurrent_requests,
                "metrics": {
                    "latency_ms": result.metrics.latency_ms,
                    "tokens_per_second": result.metrics.tokens_per_second,
                    "requests_per_second": result.metrics.requests_per_second,
                    "success_rate": result.metrics.success_rate,
                    "error_count": result.metrics.error_count,
                    "total_requests": result.metrics.total_requests,
                    "total_tokens": result.metrics.total_tokens,
                    "avg_response_length": result.metrics.avg_response_length,
                },
                "errors": result.errors,
            }
            results_data.append(result_dict)

        with open(filepath, "w") as f:
            json.dump(results_data, f, indent=2)

    async def run(self) -> PerformanceResults:
        """
        Run the performance benchmark with default settings.

        Returns:
            Performance results summary
        """
        if not self.switch:
            raise ValueError("No switch instance provided")

        # Use default providers and models if not specified
        providers = ["test_provider"]
        models = ["test_model"]

        results = await self.run_benchmark(providers, models, self.switch)

        # Calculate summary metrics
        if not results:
            return PerformanceResults(
                avg_latency=0.0,
                throughput=0.0,
                success_rate=0.0,
                provider_metrics={},
                total_requests=0,
                total_errors=0,
                avg_tokens_per_second=0.0,
            )

        # Calculate aggregate metrics
        all_latencies = [r.metrics.latency_ms for r in results]
        all_success_rates = [r.metrics.success_rate for r in results]
        all_tokens_per_second = [r.metrics.tokens_per_second for r in results]

        avg_latency = statistics.mean(all_latencies) if all_latencies else 0.0
        avg_success_rate = (
            statistics.mean(all_success_rates) if all_success_rates else 0.0
        )
        avg_tokens_per_second = (
            statistics.mean(all_tokens_per_second) if all_tokens_per_second else 0.0
        )

        # Calculate throughput (requests per second)
        total_requests = sum(r.metrics.total_requests for r in results)
        total_errors = sum(r.metrics.error_count for r in results)
        total_time = (
            sum(all_latencies) / 1000.0 if all_latencies else 1.0
        )  # Convert to seconds
        throughput = total_requests / total_time if total_time > 0 else 0.0

        # Create provider metrics
        provider_metrics = {}
        for result in results:
            provider = result.provider
            if provider not in provider_metrics:
                provider_metrics[provider] = {}
            provider_metrics[provider] = {
                "latency_ms": result.metrics.latency_ms,
                "success_rate": result.metrics.success_rate,
                "tokens_per_second": result.metrics.tokens_per_second,
                "total_requests": result.metrics.total_requests,
                "error_count": result.metrics.error_count,
            }

        return PerformanceResults(
            avg_latency=avg_latency,
            throughput=throughput,
            success_rate=avg_success_rate,
            provider_metrics=provider_metrics,
            total_requests=total_requests,
            total_errors=total_errors,
            avg_tokens_per_second=avg_tokens_per_second,
        )
