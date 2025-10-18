"""
Performance monitor for real-time LLM performance tracking.

This module provides real-time monitoring of LLM performance metrics,
including latency, success rates, and quality scores.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json
import threading
from enum import Enum


class PerformanceMetric(str, Enum):
    """Types of performance metrics tracked."""

    LATENCY = "latency"
    SUCCESS_RATE = "success_rate"
    QUALITY_SCORE = "quality_score"
    COST_EFFICIENCY = "cost_efficiency"
    AVAILABILITY = "availability"


@dataclass
class PerformanceSnapshot:
    """Snapshot of performance metrics at a point in time."""

    timestamp: datetime
    provider: str
    model: str
    latency_ms: float
    success: bool
    quality_score: Optional[float] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class PerformanceStats:
    """Aggregated performance statistics."""

    provider: str
    model: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    avg_quality_score: float = 0.0
    total_cost: float = 0.0
    avg_cost_per_request: float = 0.0
    success_rate: float = 0.0
    availability_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """
    Real-time performance monitoring for LLM providers.

    This class tracks performance metrics, calculates statistics,
    and provides insights for intelligent switching decisions.
    """

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.performance_history: deque = deque(maxlen=history_size)
        self.stats_cache: Dict[str, PerformanceStats] = {}
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()

        # Initialize default alert thresholds
        self._initialize_alert_thresholds()

    def _initialize_alert_thresholds(self) -> None:
        """Initialize default alert thresholds."""
        self.alert_thresholds = {
            "latency_ms": {"warning": 5000, "critical": 10000},
            "success_rate": {"warning": 0.95, "critical": 0.90},
            "availability": {"warning": 0.98, "critical": 0.95},
        }

    def record_request(
        self,
        provider: str,
        model: str,
        latency_ms: float,
        success: bool,
        quality_score: Optional[float] = None,
        cost: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Record a request performance snapshot."""
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            success=success,
            quality_score=quality_score,
            cost=cost,
            error_message=error_message,
        )

        with self._lock:
            self.performance_history.append(snapshot)
            # Invalidate stats cache for this provider:model
            cache_key = f"{provider}:{model}"
            if cache_key in self.stats_cache:
                del self.stats_cache[cache_key]

    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a generic metric."""
        # For now, we'll store this as a simple dictionary
        # In a real implementation, you might want a more sophisticated metric storage
        with self._lock:
            # Create a simple metric record
            metric_record = {
                "timestamp": datetime.now(),
                "metric_name": metric_name,
                "value": value,
                "tags": tags or {},
            }
            # Store in a simple list for now
            if not hasattr(self, "generic_metrics"):
                self.generic_metrics = []
            self.generic_metrics.append(metric_record)

    def get_performance_stats(
        self, provider: str, model: str, time_window: Optional[timedelta] = None
    ) -> PerformanceStats:
        """Get performance statistics for a specific provider and model."""
        cache_key = f"{provider}:{model}"

        with self._lock:
            # Check cache first
            if cache_key in self.stats_cache:
                cached_stats = self.stats_cache[cache_key]
                # Check if cache is still valid (less than 1 minute old)
                if datetime.now() - cached_stats.last_updated < timedelta(minutes=1):
                    return cached_stats

            # Calculate fresh stats
            stats = self._calculate_stats(provider, model, time_window)
            self.stats_cache[cache_key] = stats
            return stats

    def _calculate_stats(
        self, provider: str, model: str, time_window: Optional[timedelta] = None
    ) -> PerformanceStats:
        """Calculate performance statistics from history."""
        # Filter snapshots for this provider and model
        snapshots = [
            s
            for s in self.performance_history
            if s.provider == provider and s.model == model
        ]

        # Apply time window filter if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            snapshots = [s for s in snapshots if s.timestamp >= cutoff_time]

        if not snapshots:
            return PerformanceStats(provider=provider, model=model)

        # Calculate basic statistics
        total_requests = len(snapshots)
        successful_requests = sum(1 for s in snapshots if s.success)
        failed_requests = total_requests - successful_requests
        success_rate = (
            successful_requests / total_requests if total_requests > 0 else 0.0
        )

        # Latency statistics
        latencies = [s.latency_ms for s in snapshots]
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        min_latency = min(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 0.0

        # Percentiles
        sorted_latencies = sorted(latencies)
        p95_latency = (
            self._percentile(sorted_latencies, 95) if sorted_latencies else 0.0
        )
        p99_latency = (
            self._percentile(sorted_latencies, 99) if sorted_latencies else 0.0
        )

        # Quality score statistics
        quality_scores = [
            s.quality_score for s in snapshots if s.quality_score is not None
        ]
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0.0

        # Cost statistics
        costs = [s.cost for s in snapshots if s.cost is not None]
        total_cost = sum(costs) if costs else 0.0
        avg_cost = total_cost / total_requests if total_requests > 0 else 0.0

        # Availability score (based on recent success rate)
        recent_snapshots = [
            s for s in snapshots if s.timestamp >= datetime.now() - timedelta(hours=1)
        ]
        recent_success_rate = (
            sum(1 for s in recent_snapshots if s.success) / len(recent_snapshots)
            if recent_snapshots
            else success_rate
        )

        return PerformanceStats(
            provider=provider,
            model=model,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            avg_quality_score=avg_quality,
            total_cost=total_cost,
            avg_cost_per_request=avg_cost,
            success_rate=success_rate,
            availability_score=recent_success_rate,
            last_updated=datetime.now(),
        )

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset."""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def get_provider_ranking(
        self, metric: PerformanceMetric, time_window: Optional[timedelta] = None
    ) -> List[Tuple[str, str, float]]:
        """
        Get providers ranked by a specific metric.

        Returns:
            List of (provider, model, score) tuples sorted by metric (descending)
        """
        rankings = []
        providers_models = set()

        # Get unique provider:model combinations
        for snapshot in self.performance_history:
            providers_models.add((snapshot.provider, snapshot.model))

        for provider, model in providers_models:
            stats = self.get_performance_stats(provider, model, time_window)

            if metric == PerformanceMetric.LATENCY:
                # Lower latency is better, so we use negative value
                score = -stats.avg_latency_ms
            elif metric == PerformanceMetric.SUCCESS_RATE:
                score = stats.success_rate
            elif metric == PerformanceMetric.QUALITY_SCORE:
                score = stats.avg_quality_score
            elif metric == PerformanceMetric.COST_EFFICIENCY:
                # Higher quality per cost is better
                score = stats.avg_quality_score / max(stats.avg_cost_per_request, 0.001)
            elif metric == PerformanceMetric.AVAILABILITY:
                score = stats.availability_score
            else:
                score = 0.0

            rankings.append((provider, model, score))

        return sorted(rankings, key=lambda x: x[2], reverse=True)

    def get_health_status(self, provider: str, model: str) -> Tuple[str, List[str]]:
        """
        Get health status for a provider:model combination.

        Returns:
            (status, warnings) where status is 'healthy', 'warning', or 'critical'
        """
        stats = self.get_performance_stats(provider, model)
        warnings = []

        # Check latency
        if stats.avg_latency_ms > self.alert_thresholds["latency_ms"]["critical"]:
            return "critical", [f"Critical latency: {stats.avg_latency_ms:.0f}ms"]
        elif stats.avg_latency_ms > self.alert_thresholds["latency_ms"]["warning"]:
            warnings.append(f"High latency: {stats.avg_latency_ms:.0f}ms")

        # Check success rate
        if stats.success_rate < self.alert_thresholds["success_rate"]["critical"]:
            return "critical", [f"Critical success rate: {stats.success_rate:.1%}"]
        elif stats.success_rate < self.alert_thresholds["success_rate"]["warning"]:
            warnings.append(f"Low success rate: {stats.success_rate:.1%}")

        # Check availability
        if stats.availability_score < self.alert_thresholds["availability"]["critical"]:
            return "critical", [
                f"Critical availability: {stats.availability_score:.1%}"
            ]
        elif (
            stats.availability_score < self.alert_thresholds["availability"]["warning"]
        ):
            warnings.append(f"Low availability: {stats.availability_score:.1%}")

        if warnings:
            return "warning", warnings
        else:
            return "healthy", []

    def get_system_overview(self) -> Dict[str, Any]:
        """Get overall system performance overview."""
        providers_models = set()
        for snapshot in self.performance_history:
            providers_models.add((snapshot.provider, snapshot.model))

        overview = {
            "total_providers": len(set(p for p, m in providers_models)),
            "total_models": len(providers_models),
            "total_requests": len(self.performance_history),
            "healthy_models": 0,
            "warning_models": 0,
            "critical_models": 0,
            "provider_stats": {},
        }

        for provider, model in providers_models:
            status, warnings = self.get_health_status(provider, model)
            stats = self.get_performance_stats(provider, model)

            if status == "healthy":
                overview["healthy_models"] += 1
            elif status == "warning":
                overview["warning_models"] += 1
            else:
                overview["critical_models"] += 1

            if provider not in overview["provider_stats"]:
                overview["provider_stats"][provider] = {
                    "models": 0,
                    "total_requests": 0,
                    "avg_latency": 0.0,
                    "success_rate": 0.0,
                }

            provider_stats = overview["provider_stats"][provider]
            provider_stats["models"] += 1
            provider_stats["total_requests"] += stats.total_requests
            provider_stats["avg_latency"] = (
                provider_stats["avg_latency"] * (provider_stats["models"] - 1)
                + stats.avg_latency_ms
            ) / provider_stats["models"]
            provider_stats["success_rate"] = (
                provider_stats["success_rate"] * (provider_stats["models"] - 1)
                + stats.success_rate
            ) / provider_stats["models"]

        return overview

    def set_alert_threshold(self, metric: str, level: str, value: float) -> None:
        """Set alert threshold for a specific metric."""
        if metric not in self.alert_thresholds:
            self.alert_thresholds[metric] = {}

        self.alert_thresholds[metric][level] = value

    def export_performance_data(self, filepath: str) -> None:
        """Export performance history to JSON file."""
        data = {
            "performance_history": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "provider": s.provider,
                    "model": s.model,
                    "latency_ms": s.latency_ms,
                    "success": s.success,
                    "quality_score": s.quality_score,
                    "cost": s.cost,
                    "error_message": s.error_message,
                }
                for s in self.performance_history
            ],
            "alert_thresholds": self.alert_thresholds,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def import_performance_data(self, filepath: str) -> None:
        """Import performance history from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.performance_history.clear()
        for item in data.get("performance_history", []):
            snapshot = PerformanceSnapshot(
                timestamp=datetime.fromisoformat(item["timestamp"]),
                provider=item["provider"],
                model=item["model"],
                latency_ms=item["latency_ms"],
                success=item["success"],
                quality_score=item.get("quality_score"),
                cost=item.get("cost"),
                error_message=item.get("error_message"),
            )
            self.performance_history.append(snapshot)

        self.alert_thresholds = data.get("alert_thresholds", {})
        self.stats_cache.clear()  # Clear cache after import
