"""
Real-time metrics collection and aggregation for LLM-Dispatcher.

This module provides comprehensive metrics collection including performance,
cost, usage, and quality metrics with real-time aggregation and streaming.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics collected."""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COST = "cost"
    QUALITY = "quality"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    USAGE = "usage"
    CUSTOM = "custom"


@dataclass
class MetricPoint:
    """A single metric data point."""

    timestamp: datetime
    metric_type: MetricType
    provider: str
    model: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Aggregated metric data."""

    metric_type: MetricType
    provider: str
    model: str
    count: int
    sum: float
    min: float
    max: float
    avg: float
    p50: float
    p95: float
    p99: float
    window_start: datetime
    window_end: datetime


class MetricsCollector:
    """
    Real-time metrics collection and aggregation system.

    This class collects metrics from various sources, aggregates them in real-time,
    and provides streaming access to metric data for monitoring and alerting.
    """

    def __init__(self, retention_hours: int = 24, aggregation_window_seconds: int = 60):
        self.retention_hours = retention_hours
        self.aggregation_window_seconds = aggregation_window_seconds

        # Metric storage
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.aggregations: Dict[str, MetricAggregation] = {}

        # Real-time streams
        self.metric_streams: Dict[str, List[Callable]] = defaultdict(list)
        self.alert_callbacks: List[Callable] = []

        # Background tasks
        self._aggregation_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        # Thread safety
        self._lock = threading.Lock()

    async def start(self) -> None:
        """Start the metrics collector background tasks."""
        if self._running:
            return

        self._running = True
        self._aggregation_task = asyncio.create_task(self._aggregation_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Metrics collector started")

    async def stop(self) -> None:
        """Stop the metrics collector background tasks."""
        self._running = False

        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Metrics collector stopped")

    def record_metric(
        self,
        metric_type: MetricType,
        provider: str,
        model: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a metric point."""
        metric = MetricPoint(
            timestamp=datetime.now(),
            metric_type=metric_type,
            provider=provider,
            model=model,
            value=value,
            tags=tags or {},
            metadata=metadata or {},
        )

        with self._lock:
            self.metrics_buffer.append(metric)

        # Notify real-time streams
        self._notify_streams(metric)

    def record_request_metrics(
        self,
        provider: str,
        model: str,
        latency_ms: float,
        success: bool,
        cost: Optional[float] = None,
        quality_score: Optional[float] = None,
        tokens_used: Optional[int] = None,
    ) -> None:
        """Record comprehensive request metrics."""
        now = datetime.now()

        # Latency
        self.record_metric(MetricType.LATENCY, provider, model, latency_ms)

        # Success/Error rate
        self.record_metric(
            MetricType.ERROR_RATE, provider, model, 0.0 if success else 1.0
        )

        # Cost
        if cost is not None:
            self.record_metric(MetricType.COST, provider, model, cost)

        # Quality
        if quality_score is not None:
            self.record_metric(MetricType.QUALITY, provider, model, quality_score)

        # Usage (tokens)
        if tokens_used is not None:
            self.record_metric(MetricType.USAGE, provider, model, float(tokens_used))

        # Throughput (requests per minute)
        self.record_metric(MetricType.THROUGHPUT, provider, model, 1.0)

    def subscribe_to_metric_stream(
        self, metric_type: MetricType, callback: Callable[[MetricPoint], None]
    ) -> None:
        """Subscribe to real-time metric stream."""
        self.metric_streams[metric_type.value].append(callback)

    def subscribe_to_alerts(
        self, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to metric alerts."""
        self.alert_callbacks.append(callback)

    def _notify_streams(self, metric: MetricPoint) -> None:
        """Notify subscribers of new metric data."""
        callbacks = self.metric_streams.get(metric.metric_type.value, [])
        for callback in callbacks:
            try:
                callback(metric)
            except Exception as e:
                logger.error(f"Error in metric stream callback: {e}")

    async def get_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[MetricPoint]:
        """Get filtered metrics."""
        with self._lock:
            metrics = list(self.metrics_buffer)

        # Apply filters
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        if provider:
            metrics = [m for m in metrics if m.provider == provider]
        if model:
            metrics = [m for m in metrics if m.model == model]
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return sorted(metrics, key=lambda x: x.timestamp)

    async def get_aggregated_metrics(
        self,
        metric_type: MetricType,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        window_minutes: int = 5,
    ) -> List[MetricAggregation]:
        """Get aggregated metrics for the specified time window."""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=window_minutes)

        metrics = await self.get_metrics(
            metric_type=metric_type,
            provider=provider,
            model=model,
            start_time=start_time,
            end_time=end_time,
        )

        # Group by provider:model
        groups = defaultdict(list)
        for metric in metrics:
            key = f"{metric.provider}:{metric.model}"
            groups[key].append(metric)

        aggregations = []
        for key, group_metrics in groups.items():
            if not group_metrics:
                continue

            values = [m.value for m in group_metrics]
            values.sort()

            agg = MetricAggregation(
                metric_type=metric_type,
                provider=group_metrics[0].provider,
                model=group_metrics[0].model,
                count=len(values),
                sum=sum(values),
                min=min(values),
                max=max(values),
                avg=sum(values) / len(values),
                p50=self._percentile(values, 50),
                p95=self._percentile(values, 95),
                p99=self._percentile(values, 99),
                window_start=start_time,
                window_end=end_time,
            )
            aggregations.append(agg)

        return aggregations

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    async def _aggregation_loop(self) -> None:
        """Background task for metric aggregation."""
        while self._running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(self.aggregation_window_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}")
                await asyncio.sleep(5)

    async def _cleanup_loop(self) -> None:
        """Background task for metric cleanup."""
        while self._running:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cleanup every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)

    async def _aggregate_metrics(self) -> None:
        """Aggregate metrics for the current window."""
        # This would implement real-time aggregation logic
        # For now, we'll just update the aggregations cache
        pass

    async def _cleanup_old_metrics(self) -> None:
        """Remove old metrics beyond retention period."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)

        with self._lock:
            # Remove old metrics
            while (
                self.metrics_buffer and self.metrics_buffer[0].timestamp < cutoff_time
            ):
                self.metrics_buffer.popleft()

    def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics."""
        with self._lock:
            recent_metrics = [
                m
                for m in self.metrics_buffer
                if m.timestamp > datetime.now() - timedelta(minutes=5)
            ]

        if not recent_metrics:
            return {"status": "no_data", "message": "No recent metrics available"}

        # Calculate health indicators
        error_rates = [
            m.value for m in recent_metrics if m.metric_type == MetricType.ERROR_RATE
        ]
        avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0.0

        latencies = [
            m.value for m in recent_metrics if m.metric_type == MetricType.LATENCY
        ]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        # Determine health status
        if avg_error_rate > 0.1:  # 10% error rate
            status = "critical"
        elif avg_error_rate > 0.05 or avg_latency > 10000:  # 5% error or >10s latency
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "avg_error_rate": avg_error_rate,
            "avg_latency_ms": avg_latency,
            "total_requests": len(recent_metrics),
            "timestamp": datetime.now().isoformat(),
        }

    def export_metrics(self, filepath: str) -> None:
        """Export metrics to JSON file."""
        with self._lock:
            metrics_data = [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "metric_type": m.metric_type.value,
                    "provider": m.provider,
                    "model": m.model,
                    "value": m.value,
                    "tags": m.tags,
                    "metadata": m.metadata,
                }
                for m in self.metrics_buffer
            ]

        with open(filepath, "w") as f:
            json.dump(metrics_data, f, indent=2)

    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self._lock:
            total_metrics = len(self.metrics_buffer)

        if total_metrics == 0:
            return {"total_metrics": 0, "message": "No metrics collected"}

        # Get recent metrics (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp > recent_cutoff]

        # Group by type
        by_type = defaultdict(int)
        by_provider = defaultdict(int)
        by_model = defaultdict(int)

        for metric in recent_metrics:
            by_type[metric.metric_type.value] += 1
            by_provider[metric.provider] += 1
            by_model[f"{metric.provider}:{metric.model}"] += 1

        return {
            "total_metrics": total_metrics,
            "recent_metrics": len(recent_metrics),
            "by_type": dict(by_type),
            "by_provider": dict(by_provider),
            "by_model": dict(by_model),
            "collection_started": datetime.now().isoformat(),
        }
