"""
Advanced alerting system for LLM-Dispatcher monitoring.

This module provides comprehensive alerting capabilities including
threshold-based alerts, anomaly detection, and notification management.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(str, Enum):
    """Types of alerts."""

    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    COST = "cost"
    AVAILABILITY = "availability"


@dataclass
class AlertRule:
    """Alert rule configuration."""

    name: str
    alert_type: AlertType
    metric_type: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    severity: AlertSeverity
    duration_seconds: int = 60  # Alert must persist for this duration
    cooldown_seconds: int = 300  # Cooldown period after alert resolves
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """An active alert."""

    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    status: str = "active"  # "active", "resolved", "suppressed"
    notifications_sent: List[str] = field(default_factory=list)


class AlertManager:
    """
    Advanced alerting system for LLM-Dispatcher.

    This class provides comprehensive alerting capabilities including
    threshold-based alerts, anomaly detection, and notification management.
    """

    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []

        # Alert state tracking
        self.rule_states: Dict[str, Dict[str, Any]] = {}  # Rule name -> state
        self.last_alert_times: Dict[str, datetime] = {}  # Rule name -> last alert time

        # Notification channels
        self.notification_channels: Dict[str, Callable] = {}

        # Background tasks
        self._evaluation_task: Optional[asyncio.Task] = None
        self._running = False

        # Initialize default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                name="high_error_rate",
                alert_type=AlertType.PERFORMANCE,
                metric_type="error_rate",
                condition="gt",
                threshold=0.05,  # 5% error rate
                severity=AlertSeverity.WARNING,
                duration_seconds=60,
            ),
            AlertRule(
                name="critical_error_rate",
                alert_type=AlertType.PERFORMANCE,
                metric_type="error_rate",
                condition="gt",
                threshold=0.10,  # 10% error rate
                severity=AlertSeverity.CRITICAL,
                duration_seconds=30,
            ),
            AlertRule(
                name="high_latency",
                alert_type=AlertType.PERFORMANCE,
                metric_type="latency",
                condition="gt",
                threshold=10000,  # 10 seconds
                severity=AlertSeverity.WARNING,
                duration_seconds=120,
            ),
            AlertRule(
                name="critical_latency",
                alert_type=AlertType.PERFORMANCE,
                metric_type="latency",
                condition="gt",
                threshold=30000,  # 30 seconds
                severity=AlertSeverity.CRITICAL,
                duration_seconds=60,
            ),
            AlertRule(
                name="high_cost",
                alert_type=AlertType.COST,
                metric_type="cost",
                condition="gt",
                threshold=1.0,  # $1 per request
                severity=AlertSeverity.WARNING,
                duration_seconds=300,
            ),
            AlertRule(
                name="provider_unavailable",
                alert_type=AlertType.AVAILABILITY,
                metric_type="availability",
                condition="lt",
                threshold=0.95,  # 95% availability
                severity=AlertSeverity.CRITICAL,
                duration_seconds=60,
            ),
        ]

        for rule in default_rules:
            self.add_alert_rule(rule)

    async def start(self) -> None:
        """Start the alert manager background tasks."""
        if self._running:
            return

        self._running = True
        self._evaluation_task = asyncio.create_task(self._evaluation_loop())
        logger.info("Alert manager started")

    async def stop(self) -> None:
        """Stop the alert manager background tasks."""
        self._running = False

        if self._evaluation_task:
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass

        logger.info("Alert manager stopped")

    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.alert_rules[rule.name] = rule
        self.rule_states[rule.name] = {
            "triggered_at": None,
            "last_evaluation": None,
            "consecutive_violations": 0,
        }
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str) -> bool:
        """Remove an alert rule."""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            if rule_name in self.rule_states:
                del self.rule_states[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
            return True
        return False

    def update_alert_rule(self, rule_name: str, **kwargs) -> bool:
        """Update an alert rule."""
        if rule_name not in self.alert_rules:
            return False

        rule = self.alert_rules[rule_name]
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        logger.info(f"Updated alert rule: {rule_name}")
        return True

    def register_notification_channel(
        self, channel_name: str, callback: Callable[[Alert], None]
    ) -> None:
        """Register a notification channel."""
        self.notification_channels[channel_name] = callback
        logger.info(f"Registered notification channel: {channel_name}")

    async def evaluate_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """Evaluate metrics against alert rules."""
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            try:
                await self._evaluate_rule(rule, metrics_data)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_name}: {e}")

    async def _evaluate_rule(
        self, rule: AlertRule, metrics_data: Dict[str, Any]
    ) -> None:
        """Evaluate a single alert rule."""
        state = self.rule_states.get(rule.name, {})
        current_time = datetime.now()

        # Get metric value
        metric_value = self._get_metric_value(metrics_data, rule.metric_type)
        if metric_value is None:
            return  # No data for this metric

        # Check condition
        condition_met = self._check_condition(
            metric_value, rule.condition, rule.threshold
        )

        if condition_met:
            state["consecutive_violations"] = state.get("consecutive_violations", 0) + 1
            state["last_evaluation"] = current_time

            # Check if we should trigger an alert
            if state["consecutive_violations"] >= (
                rule.duration_seconds // 10
            ):  # Assuming 10s evaluation interval
                if not state.get("triggered_at"):
                    await self._trigger_alert(rule, metric_value, metrics_data)
                    state["triggered_at"] = current_time
        else:
            # Reset violation count
            if state.get("consecutive_violations", 0) > 0:
                await self._resolve_alert(rule.name)
            state["consecutive_violations"] = 0
            state["triggered_at"] = None

        self.rule_states[rule.name] = state

    def _get_metric_value(
        self, metrics_data: Dict[str, Any], metric_type: str
    ) -> Optional[float]:
        """Extract metric value from metrics data."""
        if metric_type == "error_rate":
            return metrics_data.get("error_rate", 0.0)
        elif metric_type == "latency":
            return metrics_data.get("avg_latency_ms", 0.0)
        elif metric_type == "cost":
            return metrics_data.get("total_cost", 0.0)
        elif metric_type == "availability":
            return metrics_data.get("availability_score", 1.0)
        elif metric_type == "throughput":
            return metrics_data.get("requests_per_minute", 0.0)
        else:
            return metrics_data.get(metric_type)

    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Check if a condition is met."""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lte":
            return value <= threshold
        elif condition == "eq":
            return value == threshold
        else:
            return False

    async def _trigger_alert(
        self, rule: AlertRule, metric_value: float, metrics_data: Dict[str, Any]
    ) -> None:
        """Trigger a new alert."""
        # Check cooldown period
        last_alert_time = self.last_alert_times.get(rule.name)
        if last_alert_time:
            cooldown_end = last_alert_time + timedelta(seconds=rule.cooldown_seconds)
            if datetime.now() < cooldown_end:
                return  # Still in cooldown period

        alert_id = f"{rule.name}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            message=self._generate_alert_message(rule, metric_value),
            details={
                "metric_type": rule.metric_type,
                "metric_value": metric_value,
                "threshold": rule.threshold,
                "condition": rule.condition,
                "metrics_data": metrics_data,
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_times[rule.name] = datetime.now()

        # Send notifications
        await self._send_notifications(alert, rule)

        logger.warning(f"Alert triggered: {alert.message}")

    async def _resolve_alert(self, rule_name: str) -> None:
        """Resolve alerts for a rule."""
        alerts_to_resolve = [
            alert
            for alert in self.active_alerts.values()
            if alert.rule_name == rule_name and alert.status == "active"
        ]

        for alert in alerts_to_resolve:
            alert.status = "resolved"
            alert.updated_at = datetime.now()
            del self.active_alerts[alert.id]

        if alerts_to_resolve:
            logger.info(
                f"Resolved {len(alerts_to_resolve)} alerts for rule: {rule_name}"
            )

    def _generate_alert_message(self, rule: AlertRule, metric_value: float) -> str:
        """Generate alert message."""
        if rule.alert_type == AlertType.PERFORMANCE:
            if rule.metric_type == "error_rate":
                return f"High error rate: {metric_value:.2%} (threshold: {rule.threshold:.2%})"
            elif rule.metric_type == "latency":
                return f"High latency: {metric_value:.0f}ms (threshold: {rule.threshold:.0f}ms)"
        elif rule.alert_type == AlertType.COST:
            return f"High cost: ${metric_value:.4f} (threshold: ${rule.threshold:.4f})"
        elif rule.alert_type == AlertType.AVAILABILITY:
            return f"Low availability: {metric_value:.2%} (threshold: {rule.threshold:.2%})"
        else:
            return f"Alert triggered: {rule.metric_type} = {metric_value} {rule.condition} {rule.threshold}"

    async def _send_notifications(self, alert: Alert, rule: AlertRule) -> None:
        """Send notifications for an alert."""
        for channel_name in rule.notification_channels:
            if channel_name in self.notification_channels:
                try:
                    await self.notification_channels[channel_name](alert)
                    alert.notifications_sent.append(channel_name)
                except Exception as e:
                    logger.error(f"Error sending notification via {channel_name}: {e}")

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [
            {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "details": alert.details,
                "created_at": alert.created_at.isoformat(),
                "updated_at": alert.updated_at.isoformat(),
                "status": alert.status,
            }
            for alert in self.active_alerts.values()
        ]

    async def get_alert_history(
        self, limit: int = 100, severity: Optional[AlertSeverity] = None
    ) -> List[Dict[str, Any]]:
        """Get alert history."""
        alerts = self.alert_history[-limit:] if limit else self.alert_history

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return [
            {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
                "updated_at": alert.updated_at.isoformat(),
                "status": alert.status,
            }
            for alert in alerts
        ]

    async def suppress_alert(self, alert_id: str, duration_minutes: int = 60) -> bool:
        """Suppress an alert for a specified duration."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.status = "suppressed"
        alert.updated_at = datetime.now()

        # Schedule unsuppression
        asyncio.create_task(self._unsuppress_alert(alert_id, duration_minutes))

        logger.info(f"Suppressed alert {alert_id} for {duration_minutes} minutes")
        return True

    async def _unsuppress_alert(self, alert_id: str, duration_minutes: int) -> None:
        """Unsuppress an alert after duration."""
        await asyncio.sleep(duration_minutes * 60)

        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            if alert.status == "suppressed":
                alert.status = "active"
                alert.updated_at = datetime.now()
                logger.info(f"Unsuppressed alert {alert_id}")

    async def _evaluation_loop(self) -> None:
        """Background task for continuous alert evaluation."""
        while self._running:
            try:
                # This would be called with real metrics data
                # For now, we'll just sleep
                await asyncio.sleep(10)  # Evaluate every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(5)

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert system status."""
        active_count = len(self.active_alerts)
        total_rules = len(self.alert_rules)
        enabled_rules = len([r for r in self.alert_rules.values() if r.enabled])

        severity_counts = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "active_alerts": active_count,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "severity_breakdown": severity_counts,
            "notification_channels": list(self.notification_channels.keys()),
            "last_updated": datetime.now().isoformat(),
        }
