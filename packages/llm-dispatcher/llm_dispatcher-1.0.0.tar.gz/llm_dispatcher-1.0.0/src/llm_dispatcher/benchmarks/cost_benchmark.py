"""
Cost benchmark implementations for LLM evaluation.

This module provides cost benchmarking tools for measuring and comparing
the cost efficiency of different LLM providers and models.
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
class CostResults:
    """Results from cost benchmark evaluation."""

    avg_cost: float
    cost_per_token: float
    tokens_per_dollar: float
    provider_metrics: Dict[str, Dict[str, Any]]
    total_cost: float
    total_tokens: int
    most_cost_effective: str


@dataclass
class CostMetrics:
    """Cost metrics for a single benchmark run."""

    total_cost: float
    cost_per_token: float
    cost_per_request: float
    tokens_per_dollar: float
    requests_per_dollar: float
    total_tokens: int
    total_requests: int
    avg_tokens_per_request: float


@dataclass
class CostBenchmarkResult:
    """Result of a cost benchmark run."""

    provider: str
    model: str
    metrics: CostMetrics
    timestamp: datetime
    test_prompts: List[str]
    iterations: int
    errors: List[str] = field(default_factory=list)


class CostBenchmark:
    """
    Cost benchmark for measuring and comparing LLM pricing.

    This class provides comprehensive cost analysis capabilities including
    per-token pricing, per-request costs, and cost efficiency comparisons.
    """

    def __init__(
        self,
        test_prompts: List[str],
        iterations: int = 1,
        switch: Optional[LLMProvider] = None,
    ):
        """
        Initialize cost benchmark.

        Args:
            test_prompts: List of test prompts to use for benchmarking
            iterations: Number of iterations to run for each prompt
            switch: LLM switch instance to use for testing
        """
        if not test_prompts:
            raise ValueError("test_prompts cannot be empty")
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        self.test_prompts = test_prompts
        self.iterations = iterations
        self.switch = switch
        self.results: List[CostBenchmarkResult] = []

    async def run_benchmark(
        self,
        providers: List[str],
        models: List[str],
        switch: Optional[LLMProvider] = None,
    ) -> List[CostBenchmarkResult]:
        """
        Run cost benchmark across multiple providers and models.

        Args:
            providers: List of provider names to test
            models: List of model names to test
            switch: LLM switch instance (overrides instance switch)

        Returns:
            List of cost benchmark results
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
                    error_result = CostBenchmarkResult(
                        provider=provider,
                        model=model,
                        metrics=CostMetrics(
                            total_cost=0.0,
                            cost_per_token=0.0,
                            cost_per_request=0.0,
                            tokens_per_dollar=0.0,
                            requests_per_dollar=0.0,
                            total_tokens=0,
                            total_requests=0,
                            avg_tokens_per_request=0.0,
                        ),
                        timestamp=datetime.now(),
                        test_prompts=self.test_prompts,
                        iterations=self.iterations,
                        errors=[str(e)],
                    )
                    results.append(error_result)

        self.results.extend(results)
        return results

    async def _run_single_benchmark(
        self, provider: str, model: str, switch: LLMProvider
    ) -> CostBenchmarkResult:
        """Run cost benchmark for a single provider/model combination."""

        total_cost = 0.0
        total_tokens = 0
        total_requests = 0
        errors = []

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

        # Process each request
        for request in all_requests:
            try:
                response = await switch.process_request(request)

                if response and response.content:
                    # Estimate token count (rough approximation)
                    token_count = len(response.content.split())
                    total_tokens += token_count

                    # Get cost from response metadata or calculate
                    if hasattr(response, "cost") and response.cost is not None:
                        total_cost += response.cost
                    else:
                        # Fallback: estimate cost based on provider/model
                        estimated_cost = self._estimate_cost(
                            provider, model, token_count
                        )
                        total_cost += estimated_cost

            except Exception as e:
                errors.append(f"Error processing request: {str(e)}")

        # Calculate cost metrics
        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0.0
        cost_per_request = total_cost / total_requests if total_requests > 0 else 0.0
        tokens_per_dollar = total_tokens / total_cost if total_cost > 0 else 0.0
        requests_per_dollar = total_requests / total_cost if total_cost > 0 else 0.0
        avg_tokens_per_request = (
            total_tokens / total_requests if total_requests > 0 else 0.0
        )

        metrics = CostMetrics(
            total_cost=total_cost,
            cost_per_token=cost_per_token,
            cost_per_request=cost_per_request,
            tokens_per_dollar=tokens_per_dollar,
            requests_per_dollar=requests_per_dollar,
            total_tokens=total_tokens,
            total_requests=total_requests,
            avg_tokens_per_request=avg_tokens_per_request,
        )

        return CostBenchmarkResult(
            provider=provider,
            model=model,
            metrics=metrics,
            timestamp=datetime.now(),
            test_prompts=self.test_prompts,
            iterations=self.iterations,
            errors=errors,
        )

    def _estimate_cost(self, provider: str, model: str, token_count: int) -> float:
        """
        Estimate cost based on provider and model.

        This is a fallback method when actual cost data is not available.
        In a real implementation, this would use actual pricing data.
        """
        # Rough cost estimates (these should be updated with real pricing)
        pricing = {
            "openai": {
                "gpt-4": 0.00003,  # per token
                "gpt-3.5-turbo": 0.000002,
                "default": 0.00001,
            },
            "anthropic": {
                "claude-3-opus": 0.000015,
                "claude-3-sonnet": 0.000003,
                "claude-3-haiku": 0.00000025,
                "default": 0.000005,
            },
            "google": {"gemini-pro": 0.000001, "default": 0.000001},
            "default": 0.00001,
        }

        provider_pricing = pricing.get(provider, pricing["default"])
        cost_per_token = provider_pricing.get(
            model, provider_pricing.get("default", 0.00001)
        )

        return token_count * cost_per_token

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all cost benchmark results."""
        if not self.results:
            return {}

        all_costs = [r.metrics.total_cost for r in self.results]
        all_cost_per_token = [r.metrics.cost_per_token for r in self.results]
        all_tokens_per_dollar = [r.metrics.tokens_per_dollar for r in self.results]

        return {
            "total_benchmarks": len(self.results),
            "avg_total_cost": statistics.mean(all_costs),
            "min_total_cost": min(all_costs),
            "max_total_cost": max(all_costs),
            "avg_cost_per_token": statistics.mean(all_cost_per_token),
            "avg_tokens_per_dollar": statistics.mean(all_tokens_per_dollar),
            "most_cost_effective": max(
                self.results, key=lambda r: r.metrics.tokens_per_dollar
            ),
            "least_cost_effective": min(
                self.results, key=lambda r: r.metrics.tokens_per_dollar
            ),
        }

    def compare_providers(self) -> Dict[str, Any]:
        """Compare cost efficiency across providers."""
        if not self.results:
            return {}

        provider_stats = {}
        for result in self.results:
            provider = result.provider
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "total_requests": 0,
                    "models": set(),
                }

            provider_stats[provider]["total_cost"] += result.metrics.total_cost
            provider_stats[provider]["total_tokens"] += result.metrics.total_tokens
            provider_stats[provider]["total_requests"] += result.metrics.total_requests
            provider_stats[provider]["models"].add(result.model)

        # Calculate efficiency metrics
        comparison = {}
        for provider, stats in provider_stats.items():
            stats["models"] = list(stats["models"])
            stats["cost_per_token"] = (
                stats["total_cost"] / stats["total_tokens"]
                if stats["total_tokens"] > 0
                else 0.0
            )
            stats["tokens_per_dollar"] = (
                stats["total_tokens"] / stats["total_cost"]
                if stats["total_cost"] > 0
                else 0.0
            )
            comparison[provider] = stats

        return comparison

    def save_results(self, filepath: Union[str, Path]) -> None:
        """Save cost benchmark results to a JSON file."""
        results_data = []
        for result in self.results:
            result_dict = {
                "provider": result.provider,
                "model": result.model,
                "timestamp": result.timestamp.isoformat(),
                "test_prompts": result.test_prompts,
                "iterations": result.iterations,
                "metrics": {
                    "total_cost": result.metrics.total_cost,
                    "cost_per_token": result.metrics.cost_per_token,
                    "cost_per_request": result.metrics.cost_per_request,
                    "tokens_per_dollar": result.metrics.tokens_per_dollar,
                    "requests_per_dollar": result.metrics.requests_per_dollar,
                    "total_tokens": result.metrics.total_tokens,
                    "total_requests": result.metrics.total_requests,
                    "avg_tokens_per_request": result.metrics.avg_tokens_per_request,
                },
                "errors": result.errors,
            }
            results_data.append(result_dict)

        with open(filepath, "w") as f:
            json.dump(results_data, f, indent=2)

    async def run(self) -> CostResults:
        """
        Run the cost benchmark with default settings.

        Returns:
            Cost results summary
        """
        if not self.switch:
            raise ValueError("No switch instance provided")

        # Use default providers and models if not specified
        providers = ["test_provider"]
        models = ["test_model"]

        results = await self.run_benchmark(providers, models, self.switch)

        # Calculate summary metrics
        if not results:
            return CostResults(
                avg_cost=0.0,
                cost_per_token=0.0,
                tokens_per_dollar=0.0,
                provider_metrics={},
                total_cost=0.0,
                total_tokens=0,
                most_cost_effective="",
            )

        # Calculate aggregate metrics
        all_costs = [r.metrics.total_cost for r in results]
        all_cost_per_token = [r.metrics.cost_per_token for r in results]
        all_tokens_per_dollar = [r.metrics.tokens_per_dollar for r in results]

        avg_cost = statistics.mean(all_costs) if all_costs else 0.0
        avg_cost_per_token = (
            statistics.mean(all_cost_per_token) if all_cost_per_token else 0.0
        )
        avg_tokens_per_dollar = (
            statistics.mean(all_tokens_per_dollar) if all_tokens_per_dollar else 0.0
        )

        # Calculate totals
        total_cost = sum(r.metrics.total_cost for r in results)
        total_tokens = sum(r.metrics.total_tokens for r in results)

        # Find most cost effective provider
        most_cost_effective = (
            max(results, key=lambda r: r.metrics.tokens_per_dollar).provider
            if results
            else ""
        )

        # Create provider metrics
        provider_metrics = {}
        for result in results:
            provider = result.provider
            if provider not in provider_metrics:
                provider_metrics[provider] = {}
            provider_metrics[provider] = {
                "total_cost": result.metrics.total_cost,
                "cost_per_token": result.metrics.cost_per_token,
                "tokens_per_dollar": result.metrics.tokens_per_dollar,
                "total_tokens": result.metrics.total_tokens,
                "total_requests": result.metrics.total_requests,
            }

        return CostResults(
            avg_cost=avg_cost,
            cost_per_token=avg_cost_per_token,
            tokens_per_dollar=avg_tokens_per_dollar,
            provider_metrics=provider_metrics,
            total_cost=total_cost,
            total_tokens=total_tokens,
            most_cost_effective=most_cost_effective,
        )
