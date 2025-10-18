"""
Real-time dashboard for LLM-Dispatcher monitoring.

This module provides a comprehensive dashboard for monitoring system performance,
usage patterns, and health metrics in real-time.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import logging

from .analytics import AnalyticsEngine, PerformanceReport, UsagePattern, SystemHealth
from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """
    Comprehensive monitoring dashboard for LLM-Dispatcher.

    This class provides a real-time dashboard with multiple widgets
    for monitoring system performance, usage patterns, and health.
    """

    def __init__(
        self,
        analytics_engine: AnalyticsEngine,
        metrics_collector: MetricsCollector,
        update_interval: int = 30,
    ):
        self.analytics_engine = analytics_engine
        self.metrics_collector = metrics_collector
        self.update_interval = update_interval

        # Dashboard state
        self.is_running = False
        self.dashboard_data = {}
        self.subscribers = []

    async def start(self):
        """Start the dashboard."""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting monitoring dashboard")

        # Start background update task
        asyncio.create_task(self._update_loop())

    async def stop(self):
        """Stop the dashboard."""
        self.is_running = False
        logger.info("Stopping monitoring dashboard")

    async def _update_loop(self):
        """Main update loop for the dashboard."""
        while self.is_running:
            try:
                # Update dashboard data
                await self._update_dashboard_data()

                # Wait for next update
                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _update_dashboard_data(self):
        """Update all dashboard data."""
        try:
            # Get recent performance data (last hour)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)

            # Get performance report
            report = self.analytics_engine.generate_performance_report(
                start_time, end_time
            )

            # Get system health
            health = self.analytics_engine.assess_system_health()

            # Get usage patterns
            usage_patterns = self.analytics_engine.analyze_usage_patterns(days=1)

            # Update dashboard data
            self.dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "system_overview": {
                    "total_requests": report.total_requests,
                    "success_rate": report.success_rate,
                    "average_latency": report.average_latency_ms,
                    "total_cost": report.total_cost,
                    "system_health": health.overall_health_score,
                    "system_status": health.status,
                },
                "provider_performance": {
                    "providers": list(report.provider_stats.keys()),
                    "provider_stats": report.provider_stats,
                },
                "cost_analysis": {
                    "total_cost": report.total_cost,
                    "average_cost": report.average_cost_per_request,
                    "cost_per_token": report.cost_per_token,
                },
                "error_analysis": {
                    "total_errors": report.failed_requests,
                    "error_rate": 1 - report.success_rate,
                    "error_breakdown": report.error_analysis,
                },
                "usage_patterns": {
                    "peak_hours": usage_patterns.peak_hours,
                    "quiet_hours": usage_patterns.quiet_hours,
                    "task_distribution": usage_patterns.task_distribution,
                },
            }

            # Notify subscribers
            await self._notify_subscribers()

        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")

    def subscribe(self, callback: Callable):
        """Subscribe to dashboard updates."""
        self.subscribers.append(callback)

    async def _notify_subscribers(self):
        """Notify all subscribers of dashboard updates."""
        for callback in self.subscribers:
            try:
                await callback(self.dashboard_data)
            except Exception as e:
                logger.error(f"Error notifying dashboard subscriber: {e}")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        return self.dashboard_data

    async def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of all dashboard data."""
        try:
            # Get system health
            health = self.analytics_engine.assess_system_health()

            # Get recent performance report
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            performance_report = self.analytics_engine.generate_performance_report(
                start_time, end_time
            )

            return {
                "timestamp": datetime.now().isoformat(),
                "dashboard_status": {
                    "is_running": self.is_running,
                    "update_interval": self.update_interval,
                },
                "system_health": {
                    "overall_score": health.overall_health_score,
                    "status": health.status,
                    "issues": health.issues,
                    "recommendations": health.recommendations,
                },
                "performance_summary": {
                    "total_requests": performance_report.total_requests,
                    "success_rate": performance_report.success_rate,
                    "average_latency": performance_report.average_latency_ms,
                    "total_cost": performance_report.total_cost,
                },
            }

        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return {"error": str(e)}
