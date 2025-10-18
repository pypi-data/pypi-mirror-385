"""
Benchmark analyzer for statistical analysis and comparison of benchmark results.

This module provides comprehensive analysis tools for benchmark results including
statistical analysis, provider comparisons, and performance insights.
"""

import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from .performance_benchmark import BenchmarkResult
from .cost_benchmark import CostBenchmarkResult
from .custom_benchmark import CustomBenchmarkResult


@dataclass
class StatisticalAnalysis:
    """Statistical analysis results for a set of benchmark data."""

    mean: float
    median: float
    mode: Optional[float]
    standard_deviation: float
    variance: float
    min_value: float
    max_value: float
    range: float
    quartiles: Tuple[float, float, float]  # Q1, Q2 (median), Q3
    outliers: List[float]
    sample_size: int


@dataclass
class ProviderComparison:
    """Comparison results between providers."""

    provider_rankings: Dict[str, int]
    performance_scores: Dict[str, float]
    cost_efficiency_scores: Dict[str, float]
    overall_scores: Dict[str, float]
    best_provider: str
    worst_provider: str
    recommendations: List[str]


class BenchmarkAnalyzer:
    """
    Comprehensive analyzer for benchmark results.

    This class provides statistical analysis, provider comparisons, and
    performance insights from benchmark data.
    """

    def __init__(self, results: List[Any]):
        """
        Initialize benchmark analyzer.

        Args:
            results: List of benchmark results to analyze
        """
        self.results = results
        self.performance_results: List[BenchmarkResult] = []
        self.cost_results: List[CostBenchmarkResult] = []
        self.custom_results: List[CustomBenchmarkResult] = []

        # Categorize results by type
        self._categorize_results()

    def _categorize_results(self) -> None:
        """Categorize results by their type."""
        for result in self.results:
            if isinstance(result, BenchmarkResult):
                self.performance_results.append(result)
            elif isinstance(result, CostBenchmarkResult):
                self.cost_results.append(result)
            elif isinstance(result, CustomBenchmarkResult):
                self.custom_results.append(result)

    def get_statistical_analysis(
        self, metric: str = "latency_ms"
    ) -> Dict[str, StatisticalAnalysis]:
        """
        Get statistical analysis for specified metric across all results.

        Args:
            metric: The metric to analyze (latency_ms, success_rate, etc.)

        Returns:
            Dictionary mapping result type to statistical analysis
        """
        analysis = {}

        # Analyze performance results
        if self.performance_results:
            performance_data = self._extract_performance_metric(metric)
            if performance_data:
                analysis["performance"] = self._calculate_statistics(performance_data)

        # Analyze cost results
        if self.cost_results:
            cost_data = self._extract_cost_metric(metric)
            if cost_data:
                analysis["cost"] = self._calculate_statistics(cost_data)

        # Analyze custom results
        if self.custom_results:
            custom_data = self._extract_custom_metric(metric)
            if custom_data:
                analysis["custom"] = self._calculate_statistics(custom_data)

        return analysis

    def _extract_performance_metric(self, metric: str) -> List[float]:
        """Extract specified metric from performance results."""
        data = []
        for result in self.performance_results:
            if hasattr(result.metrics, metric):
                value = getattr(result.metrics, metric)
                if isinstance(value, (int, float)):
                    data.append(float(value))
        return data

    def _extract_cost_metric(self, metric: str) -> List[float]:
        """Extract specified metric from cost results."""
        data = []
        for result in self.cost_results:
            if hasattr(result.metrics, metric):
                value = getattr(result.metrics, metric)
                if isinstance(value, (int, float)):
                    data.append(float(value))
        return data

    def _extract_custom_metric(self, metric: str) -> List[float]:
        """Extract specified metric from custom results."""
        data = []
        for result in self.custom_results:
            if hasattr(result.metrics, metric):
                value = getattr(result.metrics, metric)
                if isinstance(value, (int, float)):
                    data.append(float(value))
        return data

    def _calculate_statistics(self, data: List[float]) -> StatisticalAnalysis:
        """Calculate comprehensive statistics for a dataset."""
        if not data:
            return StatisticalAnalysis(
                mean=0.0,
                median=0.0,
                mode=None,
                standard_deviation=0.0,
                variance=0.0,
                min_value=0.0,
                max_value=0.0,
                range=0.0,
                quartiles=(0.0, 0.0, 0.0),
                outliers=[],
                sample_size=0,
            )

        # Basic statistics
        mean = statistics.mean(data)
        median = statistics.median(data)
        mode = statistics.mode(data) if len(set(data)) < len(data) else None
        stdev = statistics.stdev(data) if len(data) > 1 else 0.0
        variance = statistics.variance(data) if len(data) > 1 else 0.0
        min_value = min(data)
        max_value = max(data)
        range_val = max_value - min_value

        # Quartiles
        sorted_data = sorted(data)
        n = len(sorted_data)
        q1 = sorted_data[n // 4] if n >= 4 else sorted_data[0]
        q2 = median
        q3 = sorted_data[3 * n // 4] if n >= 4 else sorted_data[-1]

        # Outliers (using IQR method)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        return StatisticalAnalysis(
            mean=mean,
            median=median,
            mode=mode,
            standard_deviation=stdev,
            variance=variance,
            min_value=min_value,
            max_value=max_value,
            range=range_val,
            quartiles=(q1, q2, q3),
            outliers=outliers,
            sample_size=len(data),
        )

    def compare_providers(self) -> ProviderComparison:
        """
        Compare providers across all benchmark types.

        Returns:
            Provider comparison results
        """
        provider_scores = {}
        provider_performance = {}
        provider_cost_efficiency = {}

        # Analyze performance results
        for result in self.performance_results:
            provider = result.provider
            if provider not in provider_scores:
                provider_scores[provider] = []
                provider_performance[provider] = []
                provider_cost_efficiency[provider] = []

            # Performance score (higher success rate, lower latency is better)
            performance_score = result.metrics.success_rate * (
                1000 / max(result.metrics.latency_ms, 1)
            )
            provider_performance[provider].append(performance_score)
            provider_scores[provider].append(performance_score)

        # Analyze cost results
        for result in self.cost_results:
            provider = result.provider
            if provider not in provider_scores:
                provider_scores[provider] = []
                provider_performance[provider] = []
                provider_cost_efficiency[provider] = []

            # Cost efficiency score (more tokens per dollar is better)
            cost_efficiency_score = result.metrics.tokens_per_dollar
            provider_cost_efficiency[provider].append(cost_efficiency_score)
            provider_scores[provider].append(cost_efficiency_score)

        # Analyze custom results
        for result in self.custom_results:
            provider = result.provider
            if provider not in provider_scores:
                provider_scores[provider] = []
                provider_performance[provider] = []
                provider_cost_efficiency[provider] = []

            # Custom score (higher success rate and score is better)
            custom_score = result.metrics.success_rate * result.metrics.avg_score
            provider_scores[provider].append(custom_score)

        # Calculate average scores per provider
        avg_performance_scores = {
            provider: statistics.mean(scores) if scores else 0.0
            for provider, scores in provider_performance.items()
        }

        avg_cost_efficiency_scores = {
            provider: statistics.mean(scores) if scores else 0.0
            for provider, scores in provider_cost_efficiency.items()
        }

        avg_overall_scores = {
            provider: statistics.mean(scores) if scores else 0.0
            for provider, scores in provider_scores.items()
        }

        # Rank providers
        sorted_providers = sorted(
            avg_overall_scores.items(), key=lambda x: x[1], reverse=True
        )
        provider_rankings = {
            provider: rank + 1 for rank, (provider, _) in enumerate(sorted_providers)
        }

        # Find best and worst providers
        best_provider = sorted_providers[0][0] if sorted_providers else ""
        worst_provider = sorted_providers[-1][0] if sorted_providers else ""

        # Generate recommendations
        recommendations = self._generate_recommendations(
            avg_performance_scores, avg_cost_efficiency_scores, avg_overall_scores
        )

        return ProviderComparison(
            provider_rankings=provider_rankings,
            performance_scores=avg_performance_scores,
            cost_efficiency_scores=avg_cost_efficiency_scores,
            overall_scores=avg_overall_scores,
            best_provider=best_provider,
            worst_provider=worst_provider,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        performance_scores: Dict[str, float],
        cost_efficiency_scores: Dict[str, float],
        overall_scores: Dict[str, float],
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []

        if not overall_scores:
            return ["No benchmark data available for recommendations"]

        # Find best performers in each category
        best_performance = (
            max(performance_scores.items(), key=lambda x: x[1])
            if performance_scores
            else None
        )
        best_cost_efficiency = (
            max(cost_efficiency_scores.items(), key=lambda x: x[1])
            if cost_efficiency_scores
            else None
        )
        best_overall = max(overall_scores.items(), key=lambda x: x[1])

        if best_performance:
            recommendations.append(
                f"For best performance: Use {best_performance[0]} "
                f"(score: {best_performance[1]:.2f})"
            )

        if best_cost_efficiency:
            recommendations.append(
                f"For cost efficiency: Use {best_cost_efficiency[0]} "
                f"({best_cost_efficiency[1]:.0f} tokens per dollar)"
            )

        recommendations.append(
            f"For overall best results: Use {best_overall[0]} "
            f"(overall score: {best_overall[1]:.2f})"
        )

        # Performance vs cost analysis
        if performance_scores and cost_efficiency_scores:
            # Find providers that are good at both
            balanced_providers = []
            for provider in performance_scores:
                if provider in cost_efficiency_scores:
                    perf_score = performance_scores[provider]
                    cost_score = cost_efficiency_scores[provider]
                    # Normalize scores (0-1) and find balanced providers
                    max_perf = max(performance_scores.values())
                    max_cost = max(cost_efficiency_scores.values())
                    norm_perf = perf_score / max_perf if max_perf > 0 else 0
                    norm_cost = cost_score / max_cost if max_cost > 0 else 0
                    balance_score = (norm_perf + norm_cost) / 2
                    balanced_providers.append((provider, balance_score))

            if balanced_providers:
                best_balanced = max(balanced_providers, key=lambda x: x[1])
                recommendations.append(
                    f"For balanced performance and cost: Use {best_balanced[0]} "
                    f"(balance score: {best_balanced[1]:.2f})"
                )

        return recommendations

    def get_performance_insights(self) -> Dict[str, Any]:
        """Get detailed performance insights from benchmark results."""
        insights = {
            "total_benchmarks": len(self.results),
            "performance_benchmarks": len(self.performance_results),
            "cost_benchmarks": len(self.cost_results),
            "custom_benchmarks": len(self.custom_results),
        }

        # Performance insights
        if self.performance_results:
            latencies = [r.metrics.latency_ms for r in self.performance_results]
            success_rates = [r.metrics.success_rate for r in self.performance_results]

            insights["performance_insights"] = {
                "avg_latency_ms": statistics.mean(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "avg_success_rate": statistics.mean(success_rates),
                "min_success_rate": min(success_rates),
                "max_success_rate": max(success_rates),
                "fastest_provider": min(
                    self.performance_results, key=lambda r: r.metrics.latency_ms
                ).provider,
                "most_reliable_provider": max(
                    self.performance_results, key=lambda r: r.metrics.success_rate
                ).provider,
            }

        # Cost insights
        if self.cost_results:
            costs = [r.metrics.total_cost for r in self.cost_results]
            tokens_per_dollar = [r.metrics.tokens_per_dollar for r in self.cost_results]

            insights["cost_insights"] = {
                "avg_total_cost": statistics.mean(costs),
                "min_total_cost": min(costs),
                "max_total_cost": max(costs),
                "avg_tokens_per_dollar": statistics.mean(tokens_per_dollar),
                "most_cost_effective_provider": max(
                    self.cost_results, key=lambda r: r.metrics.tokens_per_dollar
                ).provider,
                "least_cost_effective_provider": min(
                    self.cost_results, key=lambda r: r.metrics.tokens_per_dollar
                ).provider,
            }

        # Custom insights
        if self.custom_results:
            scores = [r.metrics.avg_score for r in self.custom_results]
            success_rates = [r.metrics.success_rate for r in self.custom_results]

            insights["custom_insights"] = {
                "avg_score": statistics.mean(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "avg_success_rate": statistics.mean(success_rates),
                "best_performing_provider": max(
                    self.custom_results, key=lambda r: r.metrics.avg_score
                ).provider,
                "most_successful_provider": max(
                    self.custom_results, key=lambda r: r.metrics.success_rate
                ).provider,
            }

        return insights

    def save_analysis(self, filepath: Union[str, Path]) -> None:
        """Save analysis results to a JSON file."""
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "statistical_analysis": {},
            "provider_comparison": {},
            "performance_insights": self.get_performance_insights(),
        }

        # Add statistical analysis for common metrics
        for metric in [
            "latency_ms",
            "success_rate",
            "total_cost",
            "tokens_per_dollar",
            "avg_score",
        ]:
            stats = self.get_statistical_analysis(metric)
            if stats:
                analysis_data["statistical_analysis"][metric] = {
                    result_type: {
                        "mean": stats[result_type].mean,
                        "median": stats[result_type].median,
                        "mode": stats[result_type].mode,
                        "standard_deviation": stats[result_type].standard_deviation,
                        "variance": stats[result_type].variance,
                        "min_value": stats[result_type].min_value,
                        "max_value": stats[result_type].max_value,
                        "range": stats[result_type].range,
                        "quartiles": stats[result_type].quartiles,
                        "outliers": stats[result_type].outliers,
                        "sample_size": stats[result_type].sample_size,
                    }
                    for result_type in stats
                }

        # Add provider comparison
        comparison = self.compare_providers()
        analysis_data["provider_comparison"] = {
            "provider_rankings": comparison.provider_rankings,
            "performance_scores": comparison.performance_scores,
            "cost_efficiency_scores": comparison.cost_efficiency_scores,
            "overall_scores": comparison.overall_scores,
            "best_provider": comparison.best_provider,
            "worst_provider": comparison.worst_provider,
            "recommendations": comparison.recommendations,
        }

        with open(filepath, "w") as f:
            json.dump(analysis_data, f, indent=2)

    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Analyze trends in benchmark data over time.

        Returns:
            Dictionary containing trend analysis results
        """
        if not self.results:
            return {
                "trends": {},
                "summary": "No data available for trend analysis",
                "recommendations": [],
            }

        # Simple trend analysis - in a real implementation, this would analyze
        # historical data and identify patterns
        trends = {}

        # Analyze performance trends
        if len(self.results) > 1:
            # Calculate simple linear trend
            performance_values = [r.get("performance", 0) for r in self.results]
            if performance_values:
                first_half = performance_values[: len(performance_values) // 2]
                second_half = performance_values[len(performance_values) // 2 :]

                if first_half and second_half:
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)
                    trend_direction = (
                        "improving" if second_avg > first_avg else "declining"
                    )
                    trends["performance"] = {
                        "direction": trend_direction,
                        "change_percent": (
                            ((second_avg - first_avg) / first_avg * 100)
                            if first_avg > 0
                            else 0
                        ),
                    }

        return {
            "trends": trends,
            "summary": f"Analyzed {len(self.results)} benchmark results",
            "recommendations": [
                "Consider running more iterations for better trend analysis",
                "Monitor performance metrics over time",
            ],
        }
