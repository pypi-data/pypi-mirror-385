"""
Quality analysis tools for benchmark results.

This module provides statistical analysis, trend analysis, and comparative
analysis tools for quality benchmark results.
"""

import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
import json

from .quality_benchmark import QualityResults, ProviderMetrics


@dataclass
class StatisticalAnalysis:
    """Statistical analysis results."""

    mean: float
    median: float
    std: float
    variance: float
    min: float
    max: float
    p25: float
    p75: float
    p90: float
    p95: float
    p99: float
    skewness: float
    kurtosis: float


@dataclass
class DistributionAnalysis:
    """Distribution analysis results."""

    quality: Dict[str, int]
    accuracy: Dict[str, int]
    response_times: Dict[str, int]
    error_rates: Dict[str, int]


@dataclass
class TrendAnalysis:
    """Trend analysis results."""

    direction: str  # "increasing", "decreasing", "stable"
    slope: float
    r_squared: float
    confidence: float
    trend_strength: str  # "weak", "moderate", "strong"


@dataclass
class TrendResults:
    """Results from trend analysis."""

    quality: TrendAnalysis
    accuracy: TrendAnalysis
    error_rate: TrendAnalysis
    response_time: TrendAnalysis


@dataclass
class ComparativeAnalysis:
    """Comparative analysis results."""

    provider_rankings: Dict[str, int]
    model_rankings: Dict[str, int]
    task_rankings: Dict[str, int]
    performance_gaps: Dict[str, float]
    statistical_significance: Dict[str, bool]


class QualityAnalyzer:
    """
    Quality analyzer for comprehensive analysis of benchmark results.

    This class provides statistical analysis, trend analysis, and comparative
    analysis of quality benchmark results.
    """

    def __init__(self, results: QualityResults):
        """
        Initialize quality analyzer.

        Args:
            results: Quality benchmark results to analyze
        """
        self.results = results
        self.analysis_data = self._prepare_analysis_data()

    def _prepare_analysis_data(self) -> Dict[str, List[float]]:
        """Prepare data for analysis."""
        data = {
            "quality": [],
            "accuracy": [],
            "response_times": [],
            "error_rates": [],
        }

        # Extract data from provider metrics
        for provider, metrics in self.results.provider_metrics.items():
            data["quality"].append(metrics.quality_score)
            data["accuracy"].append(metrics.accuracy)
            data["response_times"].append(metrics.avg_response_time)
            data["error_rates"].append(1.0 - metrics.accuracy)

        # Extract data from task metrics
        for task, metrics in self.results.task_metrics.items():
            data["quality"].append(metrics.quality_score)
            data["accuracy"].append(metrics.accuracy)
            data["response_times"].append(metrics.avg_response_time)
            data["error_rates"].append(1.0 - metrics.accuracy)

        return data

    def get_statistical_analysis(self) -> Dict[str, StatisticalAnalysis]:
        """Get statistical analysis of quality metrics."""
        analysis = {}

        for metric, values in self.analysis_data.items():
            if not values:
                continue

            analysis[metric] = StatisticalAnalysis(
                mean=statistics.mean(values),
                median=statistics.median(values),
                std=statistics.stdev(values) if len(values) > 1 else 0.0,
                variance=statistics.variance(values) if len(values) > 1 else 0.0,
                min=min(values),
                max=max(values),
                p25=np.percentile(values, 25),
                p75=np.percentile(values, 75),
                p90=np.percentile(values, 90),
                p95=np.percentile(values, 95),
                p99=np.percentile(values, 99),
                skewness=self._calculate_skewness(values),
                kurtosis=self._calculate_kurtosis(values),
            )

        return analysis

    def get_distribution_analysis(self) -> DistributionAnalysis:
        """Get distribution analysis of quality metrics."""
        quality_dist = self._create_histogram(self.analysis_data.get("quality", []))
        accuracy_dist = self._create_histogram(self.analysis_data.get("accuracy", []))
        response_times_dist = self._create_histogram(
            self.analysis_data.get("response_times", [])
        )
        error_rates_dist = self._create_histogram(
            self.analysis_data.get("error_rates", [])
        )

        return DistributionAnalysis(
            quality=quality_dist,
            accuracy=accuracy_dist,
            response_times=response_times_dist,
            error_rates=error_rates_dist,
        )

    def get_trend_analysis(self) -> TrendResults:
        """Get trend analysis of quality metrics over time."""
        # This would typically analyze trends over time
        # For now, we'll provide placeholder trend analysis

        quality_trend = self._analyze_trend(self.analysis_data.get("quality", []))
        accuracy_trend = self._analyze_trend(self.analysis_data.get("accuracy", []))
        error_rate_trend = self._analyze_trend(
            self.analysis_data.get("error_rates", [])
        )
        response_time_trend = self._analyze_trend(
            self.analysis_data.get("response_times", [])
        )

        return TrendResults(
            quality=quality_trend,
            accuracy=accuracy_trend,
            error_rate=error_rate_trend,
            response_time=response_time_trend,
        )

    def compare_providers(self) -> Dict[str, ProviderMetrics]:
        """Compare quality across providers."""
        return self.results.provider_metrics

    def compare_models(self) -> Dict[str, Dict[str, float]]:
        """Compare quality across models."""
        # This would extract model-specific metrics
        # For now, return provider metrics as proxy
        model_metrics = {}

        for provider, metrics in self.results.provider_metrics.items():
            model_metrics[provider] = {
                "quality_score": metrics.quality_score,
                "accuracy": metrics.accuracy,
                "creative_quality": metrics.creative_quality,
                "explanatory_quality": metrics.explanatory_quality,
                "analytical_quality": metrics.analytical_quality,
                "overall_score": (
                    metrics.quality_score
                    + metrics.accuracy
                    + metrics.creative_quality
                    + metrics.explanatory_quality
                    + metrics.analytical_quality
                )
                / 5,
            }

        return model_metrics

    def compare_tasks(self) -> Dict[str, Dict[str, float]]:
        """Compare quality across task types."""
        return {
            task: {
                "quality_score": metrics.quality_score,
                "accuracy": metrics.accuracy,
                "creative_quality": metrics.creative_quality,
                "explanatory_quality": metrics.explanatory_quality,
                "analytical_quality": metrics.analytical_quality,
                "overall_score": (
                    metrics.quality_score
                    + metrics.accuracy
                    + metrics.creative_quality
                    + metrics.explanatory_quality
                    + metrics.analytical_quality
                )
                / 5,
            }
            for task, metrics in self.results.task_metrics.items()
        }

    def get_performance_gaps(self) -> Dict[str, float]:
        """Calculate performance gaps between providers."""
        gaps = {}

        if len(self.results.provider_metrics) < 2:
            return gaps

        # Calculate gaps between best and worst performers
        quality_scores = [
            m.quality_score for m in self.results.provider_metrics.values()
        ]
        accuracy_scores = [m.accuracy for m in self.results.provider_metrics.values()]

        gaps["quality_gap"] = max(quality_scores) - min(quality_scores)
        gaps["accuracy_gap"] = max(accuracy_scores) - min(accuracy_scores)

        return gaps

    def get_statistical_significance(self) -> Dict[str, bool]:
        """Test statistical significance of differences."""
        # This would perform proper statistical tests
        # For now, return placeholder results
        return {
            "provider_differences": True,
            "model_differences": True,
            "task_differences": True,
        }

    def _calculate_skewness(self, values: List[float]) -> float:
        """Calculate skewness of a distribution."""
        if len(values) < 3:
            return 0.0

        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)

        if std_val == 0:
            return 0.0

        skewness = sum(((x - mean_val) / std_val) ** 3 for x in values) / len(values)
        return skewness

    def _calculate_kurtosis(self, values: List[float]) -> float:
        """Calculate kurtosis of a distribution."""
        if len(values) < 4:
            return 0.0

        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)

        if std_val == 0:
            return 0.0

        kurtosis = (
            sum(((x - mean_val) / std_val) ** 4 for x in values) / len(values) - 3
        )
        return kurtosis

    def _create_histogram(self, values: List[float], bins: int = 10) -> Dict[str, int]:
        """Create histogram distribution."""
        if not values:
            return {}

        min_val = min(values)
        max_val = max(values)

        if min_val == max_val:
            return {f"{min_val:.2f}": len(values)}

        bin_width = (max_val - min_val) / bins
        histogram = {}

        for i in range(bins):
            bin_start = min_val + i * bin_width
            bin_end = min_val + (i + 1) * bin_width
            bin_label = f"{bin_start:.2f}-{bin_end:.2f}"

            count = sum(1 for v in values if bin_start <= v < bin_end)
            if i == bins - 1:  # Include max value in last bin
                count += sum(1 for v in values if v == max_val)

            histogram[bin_label] = count

        return histogram

    def _analyze_trend(self, values: List[float]) -> TrendAnalysis:
        """Analyze trend in a series of values."""
        if len(values) < 2:
            return TrendAnalysis(
                direction="stable",
                slope=0.0,
                r_squared=0.0,
                confidence=0.0,
                trend_strength="weak",
            )

        # Simple linear regression
        x = list(range(len(values)))
        y = values

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))

        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Determine direction and strength
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        if r_squared < 0.3:
            trend_strength = "weak"
        elif r_squared < 0.7:
            trend_strength = "moderate"
        else:
            trend_strength = "strong"

        return TrendAnalysis(
            direction=direction,
            slope=slope,
            r_squared=r_squared,
            confidence=r_squared,
            trend_strength=trend_strength,
        )

    def export_analysis(self, filepath: str) -> None:
        """Export analysis results to JSON file."""
        analysis_data = {
            "statistical_analysis": {
                metric: {
                    "mean": stats.mean,
                    "median": stats.median,
                    "std": stats.std,
                    "variance": stats.variance,
                    "min": stats.min,
                    "max": stats.max,
                    "p25": stats.p25,
                    "p75": stats.p75,
                    "p90": stats.p90,
                    "p95": stats.p95,
                    "p99": stats.p99,
                    "skewness": stats.skewness,
                    "kurtosis": stats.kurtosis,
                }
                for metric, stats in self.get_statistical_analysis().items()
            },
            "distribution_analysis": {
                "quality": self.get_distribution_analysis().quality,
                "accuracy": self.get_distribution_analysis().accuracy,
                "response_times": self.get_distribution_analysis().response_times,
                "error_rates": self.get_distribution_analysis().error_rates,
            },
            "trend_analysis": {
                "quality": {
                    "direction": self.get_trend_analysis().quality.direction,
                    "slope": self.get_trend_analysis().quality.slope,
                    "r_squared": self.get_trend_analysis().quality.r_squared,
                    "confidence": self.get_trend_analysis().quality.confidence,
                    "trend_strength": self.get_trend_analysis().quality.trend_strength,
                },
                "accuracy": {
                    "direction": self.get_trend_analysis().accuracy.direction,
                    "slope": self.get_trend_analysis().accuracy.slope,
                    "r_squared": self.get_trend_analysis().accuracy.r_squared,
                    "confidence": self.get_trend_analysis().accuracy.confidence,
                    "trend_strength": self.get_trend_analysis().accuracy.trend_strength,
                },
            },
            "performance_gaps": self.get_performance_gaps(),
            "statistical_significance": self.get_statistical_significance(),
        }

        with open(filepath, "w") as f:
            json.dump(analysis_data, f, indent=2)
