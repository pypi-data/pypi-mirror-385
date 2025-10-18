"""
Advanced analytics and reporting for LLM-Dispatcher.

This module provides comprehensive analytics, reporting, and insights
for monitoring LLM performance, usage patterns, and system health.
"""

import json
import sqlite3
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path
import statistics
from collections import defaultdict, Counter

from .metrics_collector import MetricsCollector, MetricType, MetricPoint
from ..utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


@dataclass
class PerformanceReport:
    """Comprehensive performance report."""

    # Time range
    start_time: datetime
    end_time: datetime
    duration_hours: float

    # Overall metrics
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float

    # Performance metrics
    average_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float

    # Cost metrics
    total_cost: float
    average_cost_per_request: float
    cost_per_token: float

    # Provider breakdown
    provider_stats: Dict[str, Dict[str, Any]]

    # Model breakdown
    model_stats: Dict[str, Dict[str, Any]]

    # Task type breakdown
    task_type_stats: Dict[str, Dict[str, Any]]

    # Error analysis
    error_analysis: Dict[str, int]

    # Recommendations
    recommendations: List[str]


@dataclass
class UsagePattern:
    """Usage pattern analysis."""

    # Time patterns
    peak_hours: List[int]
    quiet_hours: List[int]
    daily_pattern: Dict[str, float]  # hour -> usage

    # Provider preferences
    provider_preferences: Dict[str, float]  # provider -> percentage

    # Model preferences
    model_preferences: Dict[str, float]  # model -> percentage

    # Task distribution
    task_distribution: Dict[str, float]  # task_type -> percentage

    # Cost patterns
    cost_trends: List[Tuple[datetime, float]]
    daily_costs: Dict[str, float]  # date -> cost


@dataclass
class SystemHealth:
    """System health assessment."""

    overall_health_score: float  # 0-1
    status: str  # "healthy", "warning", "critical"

    # Component health
    provider_health: Dict[str, float]
    system_resources: Dict[str, Any]

    # Performance indicators
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    availability: Dict[str, float]

    # Issues and recommendations
    issues: List[str]
    recommendations: List[str]


class AnalyticsEngine:
    """
    Advanced analytics engine for LLM-Dispatcher.

    This class provides comprehensive analytics, reporting, and insights
    for monitoring LLM performance and system health.
    """

    def __init__(
        self,
        db_path: str = "llm_dispatcher_analytics.db",
        retention_days: int = 90,
        enable_real_time: bool = True,
    ):
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self.enable_real_time = enable_real_time

        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()

        # Database connection
        self._init_database()

        # Real-time analytics
        if self.enable_real_time:
            self._start_real_time_analytics()

    def _init_database(self):
        """Initialize analytics database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    provider TEXT,
                    model TEXT,
                    task_type TEXT,
                    success BOOLEAN,
                    latency_ms REAL,
                    cost REAL,
                    tokens_used INTEGER,
                    error_message TEXT,
                    user_id TEXT,
                    session_id TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    provider TEXT,
                    model TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    metadata TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    event_type TEXT,
                    severity TEXT,
                    message TEXT,
                    metadata TEXT
                )
            """
            )

            # Create indexes for better performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON requests(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_provider ON requests(provider)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_model ON requests(model)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_task_type ON requests(task_type)"
            )

            conn.commit()

    def _start_real_time_analytics(self):
        """Start real-time analytics processing."""
        # This would run in a background task
        logger.info("Real-time analytics started")

    async def record_request(
        self,
        provider: str,
        model: str,
        task_type: str,
        success: bool,
        latency_ms: float,
        cost: float,
        tokens_used: int = 0,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Record a request for analytics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO requests (
                        timestamp, provider, model, task_type, success,
                        latency_ms, cost, tokens_used, error_message,
                        user_id, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(),
                        provider,
                        model,
                        task_type,
                        success,
                        latency_ms,
                        cost,
                        tokens_used,
                        error_message,
                        user_id,
                        session_id,
                    ),
                )
                conn.commit()

            # Record in real-time metrics
            self.metrics_collector.record_metric(
                "request_latency", latency_ms, {"provider": provider, "model": model}
            )
            self.metrics_collector.record_metric(
                "request_cost", cost, {"provider": provider, "model": model}
            )
            self.metrics_collector.record_metric(
                "request_success", 1 if success else 0, {"provider": provider}
            )

        except Exception as e:
            logger.error(f"Error recording request: {e}")

    async def record_performance_metric(
        self,
        provider: str,
        model: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record a performance metric."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_metrics (
                        timestamp, provider, model, metric_name, metric_value, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(),
                        provider,
                        model,
                        metric_name,
                        metric_value,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                conn.commit()

            # Record in real-time metrics
            self.metrics_collector.record_metric(
                metric_name, metric_value, {"provider": provider, "model": model}
            )

        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")

    async def record_system_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Record a system event."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO system_events (
                        timestamp, event_type, severity, message, metadata
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(),
                        event_type,
                        severity,
                        message,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error recording system event: {e}")

    def generate_performance_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        providers: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        task_types: Optional[List[str]] = None,
    ) -> PerformanceReport:
        """Generate comprehensive performance report."""

        if not start_time:
            start_time = datetime.now() - timedelta(days=7)
        if not end_time:
            end_time = datetime.now()

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Build query conditions
                conditions = ["timestamp >= ?", "timestamp <= ?"]
                params = [start_time, end_time]

                if providers:
                    placeholders = ",".join("?" * len(providers))
                    conditions.append(f"provider IN ({placeholders})")
                    params.extend(providers)

                if models:
                    placeholders = ",".join("?" * len(models))
                    conditions.append(f"model IN ({placeholders})")
                    params.extend(models)

                if task_types:
                    placeholders = ",".join("?" * len(task_types))
                    conditions.append(f"task_type IN ({placeholders})")
                    params.extend(task_types)

                where_clause = " AND ".join(conditions)

                # Get overall statistics
                query = f"""
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
                        AVG(latency_ms) as avg_latency,
                        SUM(cost) as total_cost,
                        AVG(cost) as avg_cost,
                        SUM(tokens_used) as total_tokens
                    FROM requests 
                    WHERE {where_clause}
                """

                result = conn.execute(query, params).fetchone()

                total_requests = result["total_requests"] or 0
                successful_requests = result["successful_requests"] or 0
                failed_requests = result["failed_requests"] or 0
                success_rate = (
                    successful_requests / total_requests if total_requests > 0 else 0
                )

                # Get latency percentiles
                latency_query = f"""
                    SELECT latency_ms FROM requests 
                    WHERE {where_clause} AND success = 1
                    ORDER BY latency_ms
                """
                latencies = [
                    row[0] for row in conn.execute(latency_query, params).fetchall()
                ]

                median_latency = statistics.median(latencies) if latencies else 0
                p95_latency = self._percentile(latencies, 95) if latencies else 0
                p99_latency = self._percentile(latencies, 99) if latencies else 0

                # Get provider statistics
                provider_stats = self._get_provider_stats(conn, where_clause, params)

                # Get model statistics
                model_stats = self._get_model_stats(conn, where_clause, params)

                # Get task type statistics
                task_type_stats = self._get_task_type_stats(conn, where_clause, params)

                # Get error analysis
                error_analysis = self._get_error_analysis(conn, where_clause, params)

                # Generate recommendations
                recommendations = self._generate_recommendations(
                    provider_stats, model_stats, task_type_stats, success_rate
                )

                return PerformanceReport(
                    start_time=start_time,
                    end_time=end_time,
                    duration_hours=(end_time - start_time).total_seconds() / 3600,
                    total_requests=total_requests,
                    successful_requests=successful_requests,
                    failed_requests=failed_requests,
                    success_rate=success_rate,
                    average_latency_ms=result["avg_latency"] or 0,
                    median_latency_ms=median_latency,
                    p95_latency_ms=p95_latency,
                    p99_latency_ms=p99_latency,
                    total_cost=result["total_cost"] or 0,
                    average_cost_per_request=result["avg_cost"] or 0,
                    cost_per_token=(
                        result["total_cost"] / result["total_tokens"]
                        if result["total_tokens"]
                        else 0
                    ),
                    provider_stats=provider_stats,
                    model_stats=model_stats,
                    task_type_stats=task_type_stats,
                    error_analysis=error_analysis,
                    recommendations=recommendations,
                )

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            raise

    def analyze_usage_patterns(self, days: int = 30) -> UsagePattern:
        """Analyze usage patterns over time."""

        start_time = datetime.now() - timedelta(days=days)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get hourly usage patterns
                hourly_query = """
                    SELECT 
                        strftime('%H', timestamp) as hour,
                        COUNT(*) as requests,
                        AVG(latency_ms) as avg_latency
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY hour
                    ORDER BY hour
                """

                hourly_data = {}
                for row in conn.execute(hourly_query, [start_time]):
                    hourly_data[int(row["hour"])] = row["requests"]

                # Find peak and quiet hours
                if hourly_data:
                    sorted_hours = sorted(
                        hourly_data.items(), key=lambda x: x[1], reverse=True
                    )
                    peak_hours = [hour for hour, _ in sorted_hours[:3]]
                    quiet_hours = [hour for hour, _ in sorted_hours[-3:]]
                else:
                    peak_hours = []
                    quiet_hours = []

                # Get provider preferences
                provider_query = """
                    SELECT 
                        provider,
                        COUNT(*) as requests,
                        AVG(latency_ms) as avg_latency,
                        SUM(cost) as total_cost
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY provider
                """

                provider_data = {}
                total_requests = 0
                for row in conn.execute(provider_query, [start_time]):
                    provider_data[row["provider"]] = {
                        "requests": row["requests"],
                        "avg_latency": row["avg_latency"],
                        "total_cost": row["total_cost"],
                    }
                    total_requests += row["requests"]

                provider_preferences = {}
                for provider, data in provider_data.items():
                    provider_preferences[provider] = (
                        data["requests"] / total_requests if total_requests > 0 else 0
                    )

                # Get model preferences
                model_query = """
                    SELECT 
                        model,
                        COUNT(*) as requests
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY model
                """

                model_data = {}
                for row in conn.execute(model_query, [start_time]):
                    model_data[row["model"]] = row["requests"]

                model_preferences = {}
                for model, requests in model_data.items():
                    model_preferences[model] = (
                        requests / total_requests if total_requests > 0 else 0
                    )

                # Get task distribution
                task_query = """
                    SELECT 
                        task_type,
                        COUNT(*) as requests
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY task_type
                """

                task_data = {}
                for row in conn.execute(task_query, [start_time]):
                    task_data[row["task_type"]] = row["requests"]

                task_distribution = {}
                for task_type, requests in task_data.items():
                    task_distribution[task_type] = (
                        requests / total_requests if total_requests > 0 else 0
                    )

                # Get cost trends (daily)
                cost_query = """
                    SELECT 
                        DATE(timestamp) as date,
                        SUM(cost) as daily_cost
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY date
                    ORDER BY date
                """

                cost_trends = []
                daily_costs = {}
                for row in conn.execute(cost_query, [start_time]):
                    date = datetime.strptime(row["date"], "%Y-%m-%d").date()
                    cost = row["daily_cost"]
                    cost_trends.append((date, cost))
                    daily_costs[row["date"]] = cost

                return UsagePattern(
                    peak_hours=peak_hours,
                    quiet_hours=quiet_hours,
                    daily_pattern=hourly_data,
                    provider_preferences=provider_preferences,
                    model_preferences=model_preferences,
                    task_distribution=task_distribution,
                    cost_trends=cost_trends,
                    daily_costs=daily_costs,
                )

        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            raise

    def assess_system_health(self) -> SystemHealth:
        """Assess overall system health."""

        try:
            # Get recent performance data (last 24 hours)
            recent_time = datetime.now() - timedelta(hours=24)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get provider health scores
                provider_health_query = """
                    SELECT 
                        provider,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                        AVG(latency_ms) as avg_latency,
                        SUM(cost) as total_cost
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY provider
                """

                provider_health = {}
                for row in conn.execute(provider_health_query, [recent_time]):
                    provider = row["provider"]
                    total = row["total_requests"]
                    successful = row["successful_requests"]
                    avg_latency = row["avg_latency"] or 0
                    cost = row["total_cost"] or 0

                    # Calculate health score (0-1)
                    success_rate = successful / total if total > 0 else 0
                    latency_score = max(
                        0, 1 - (avg_latency / 10000)
                    )  # Penalize high latency
                    cost_score = max(0, 1 - (cost / 100))  # Penalize high cost

                    health_score = (
                        success_rate * 0.5 + latency_score * 0.3 + cost_score * 0.2
                    )
                    provider_health[provider] = health_score

                # Get system resource usage (simulated)
                system_resources = {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.1,
                    "network_usage": 12.4,
                }

                # Get response time metrics
                response_times_query = """
                    SELECT 
                        provider,
                        AVG(latency_ms) as avg_latency,
                        MIN(latency_ms) as min_latency,
                        MAX(latency_ms) as max_latency
                    FROM requests 
                    WHERE timestamp >= ? AND success = 1
                    GROUP BY provider
                """

                response_times = {}
                for row in conn.execute(response_times_query, [recent_time]):
                    response_times[row["provider"]] = {
                        "avg": row["avg_latency"],
                        "min": row["min_latency"],
                        "max": row["max_latency"],
                    }

                # Get error rates
                error_rates_query = """
                    SELECT 
                        provider,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests
                    FROM requests 
                    WHERE timestamp >= ?
                    GROUP BY provider
                """

                error_rates = {}
                for row in conn.execute(error_rates_query, [recent_time]):
                    total = row["total_requests"]
                    failed = row["failed_requests"]
                    error_rates[row["provider"]] = failed / total if total > 0 else 0

                # Calculate overall health score
                overall_health_score = (
                    sum(provider_health.values()) / len(provider_health)
                    if provider_health
                    else 0
                )

                # Determine status
                if overall_health_score >= 0.8:
                    status = "healthy"
                elif overall_health_score >= 0.6:
                    status = "warning"
                else:
                    status = "critical"

                # Generate issues and recommendations
                issues = []
                recommendations = []

                if overall_health_score < 0.8:
                    issues.append("System performance below optimal levels")
                    recommendations.append(
                        "Review provider configurations and consider load balancing"
                    )

                for provider, health in provider_health.items():
                    if health < 0.7:
                        issues.append(
                            f"Provider {provider} showing degraded performance"
                        )
                        recommendations.append(
                            f"Investigate issues with {provider} or consider fallback options"
                        )

                return SystemHealth(
                    overall_health_score=overall_health_score,
                    status=status,
                    provider_health=provider_health,
                    system_resources=system_resources,
                    response_times=response_times,
                    error_rates=error_rates,
                    availability={
                        provider: 1 - rate for provider, rate in error_rates.items()
                    },
                    issues=issues,
                    recommendations=recommendations,
                )

        except Exception as e:
            logger.error(f"Error assessing system health: {e}")
            raise

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def _get_provider_stats(
        self, conn, where_clause: str, params: List
    ) -> Dict[str, Dict[str, Any]]:
        """Get provider statistics."""
        query = f"""
            SELECT 
                provider,
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                AVG(latency_ms) as avg_latency,
                SUM(cost) as total_cost,
                AVG(cost) as avg_cost,
                SUM(tokens_used) as total_tokens
            FROM requests 
            WHERE {where_clause}
            GROUP BY provider
        """

        stats = {}
        for row in conn.execute(query, params).fetchall():
            provider = row["provider"]
            total = row["total_requests"]

            stats[provider] = {
                "total_requests": total,
                "successful_requests": row["successful_requests"],
                "failed_requests": total - row["successful_requests"],
                "success_rate": row["successful_requests"] / total if total > 0 else 0,
                "average_latency_ms": row["avg_latency"] or 0,
                "total_cost": row["total_cost"] or 0,
                "average_cost": row["avg_cost"] or 0,
                "total_tokens": row["total_tokens"] or 0,
            }

        return stats

    def _get_model_stats(
        self, conn, where_clause: str, params: List
    ) -> Dict[str, Dict[str, Any]]:
        """Get model statistics."""
        query = f"""
            SELECT 
                model,
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                AVG(latency_ms) as avg_latency,
                SUM(cost) as total_cost
            FROM requests 
            WHERE {where_clause}
            GROUP BY model
        """

        stats = {}
        for row in conn.execute(query, params).fetchall():
            model = row["model"]
            total = row["total_requests"]

            stats[model] = {
                "total_requests": total,
                "successful_requests": row["successful_requests"],
                "success_rate": row["successful_requests"] / total if total > 0 else 0,
                "average_latency_ms": row["avg_latency"] or 0,
                "total_cost": row["total_cost"] or 0,
            }

        return stats

    def _get_task_type_stats(
        self, conn, where_clause: str, params: List
    ) -> Dict[str, Dict[str, Any]]:
        """Get task type statistics."""
        query = f"""
            SELECT 
                task_type,
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                AVG(latency_ms) as avg_latency,
                SUM(cost) as total_cost
            FROM requests 
            WHERE {where_clause}
            GROUP BY task_type
        """

        stats = {}
        for row in conn.execute(query, params).fetchall():
            task_type = row["task_type"]
            total = row["total_requests"]

            stats[task_type] = {
                "total_requests": total,
                "successful_requests": row["successful_requests"],
                "success_rate": row["successful_requests"] / total if total > 0 else 0,
                "average_latency_ms": row["avg_latency"] or 0,
                "total_cost": row["total_cost"] or 0,
            }

        return stats

    def _get_error_analysis(
        self, conn, where_clause: str, params: List
    ) -> Dict[str, int]:
        """Get error analysis."""
        query = f"""
            SELECT 
                error_message,
                COUNT(*) as error_count
            FROM requests 
            WHERE {where_clause} AND success = 0 AND error_message IS NOT NULL
            GROUP BY error_message
            ORDER BY error_count DESC
        """

        error_analysis = {}
        for row in conn.execute(query, params).fetchall():
            error_analysis[row["error_message"]] = row["error_count"]

        return error_analysis

    def _generate_recommendations(
        self,
        provider_stats: Dict[str, Dict[str, Any]],
        model_stats: Dict[str, Dict[str, Any]],
        task_type_stats: Dict[str, Dict[str, Any]],
        overall_success_rate: float,
    ) -> List[str]:
        """Generate recommendations based on analytics."""
        recommendations = []

        # Provider recommendations
        for provider, stats in provider_stats.items():
            if stats["success_rate"] < 0.9:
                recommendations.append(
                    f"Consider investigating issues with {provider} - success rate: {stats['success_rate']:.1%}"
                )

            if stats["average_latency_ms"] > 5000:
                recommendations.append(
                    f"High latency detected for {provider}: {stats['average_latency_ms']:.0f}ms"
                )

        # Model recommendations
        for model, stats in model_stats.items():
            if stats["total_cost"] > 100 and stats["success_rate"] < 0.95:
                recommendations.append(
                    f"High-cost model {model} showing reliability issues"
                )

        # Overall recommendations
        if overall_success_rate < 0.95:
            recommendations.append(
                "Overall success rate below 95% - review system configuration"
            )

        # Cost optimization recommendations
        total_cost = sum(stats["total_cost"] for stats in provider_stats.values())
        if total_cost > 1000:
            recommendations.append(
                "High total cost detected - consider cost optimization strategies"
            )

        return recommendations

    def cleanup_old_data(self):
        """Clean up old data based on retention policy."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM requests WHERE timestamp < ?", [cutoff_date])
                conn.execute(
                    "DELETE FROM performance_metrics WHERE timestamp < ?", [cutoff_date]
                )
                conn.execute(
                    "DELETE FROM system_events WHERE timestamp < ?", [cutoff_date]
                )
                conn.commit()

                logger.info(f"Cleaned up data older than {self.retention_days} days")

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    def export_data(
        self, format: str = "json", file_path: Optional[str] = None
    ) -> Union[str, bytes]:
        """Export analytics data."""
        if not file_path:
            file_path = f"llm_dispatcher_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get all data
                requests = [
                    dict(row)
                    for row in conn.execute("SELECT * FROM requests").fetchall()
                ]
                performance_metrics = [
                    dict(row)
                    for row in conn.execute(
                        "SELECT * FROM performance_metrics"
                    ).fetchall()
                ]
                system_events = [
                    dict(row)
                    for row in conn.execute("SELECT * FROM system_events").fetchall()
                ]

                data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "requests": requests,
                    "performance_metrics": performance_metrics,
                    "system_events": system_events,
                }

                if format == "json":
                    with open(file_path, "w") as f:
                        json.dump(data, f, indent=2, default=str)
                    return file_path
                else:
                    raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise
