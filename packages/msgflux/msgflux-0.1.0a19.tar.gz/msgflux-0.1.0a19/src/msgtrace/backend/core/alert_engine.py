"""
Alert Evaluation Engine for msgtrace

Evaluates traces against alert conditions and triggers notifications.
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable

from .alert_models import (
    Alert,
    AlertEvent,
    AlertConditionType,
    AlertSeverity,
)
from ..storage.alert_storage import AlertStorage


class AlertEngine:
    """
    Evaluates traces against alert conditions and triggers notifications.
    """

    def __init__(
        self,
        storage: AlertStorage,
        on_alert_triggered: Optional[Callable[[AlertEvent], None]] = None
    ):
        self.storage = storage
        self.on_alert_triggered = on_alert_triggered

    async def evaluate_trace(self, trace_data: dict) -> list[AlertEvent]:
        """
        Evaluate a trace against all active alerts.

        Args:
            trace_data: Dictionary containing trace information with keys:
                - trace_id: str
                - workflow_name: Optional[str]
                - service_name: Optional[str]
                - duration_ms: float
                - span_count: int
                - error_count: int
                - total_cost: float

        Returns:
            List of triggered AlertEvents
        """
        triggered_events = []

        # Get all enabled alerts
        alerts = self.storage.list_alerts(enabled_only=True)

        for alert in alerts:
            # Check if alert matches workflow/service filters
            if not self._matches_filters(alert, trace_data):
                continue

            # Check cooldown period
            if not self._is_cooldown_expired(alert):
                continue

            # Extract value based on condition type
            value = self._extract_value(alert.condition.condition_type, trace_data)
            if value is None:
                continue

            # Evaluate condition
            if alert.condition.evaluate(value):
                event = self._create_alert_event(alert, trace_data, value)
                triggered_events.append(event)

                # Store event
                self.storage.create_alert_event(event)

                # Update alert trigger info
                alert.last_triggered_at = event.triggered_at
                alert.trigger_count += 1
                self.storage.update_alert(alert)

                # Trigger callback
                if self.on_alert_triggered:
                    try:
                        if asyncio.iscoroutinefunction(self.on_alert_triggered):
                            await self.on_alert_triggered(event)
                        else:
                            self.on_alert_triggered(event)
                    except Exception as e:
                        print(f"Error in alert callback: {e}")

        return triggered_events

    def _matches_filters(self, alert: Alert, trace_data: dict) -> bool:
        """Check if trace matches alert filters"""
        if alert.workflow_filter:
            workflow = trace_data.get("workflow_name", "")
            if not workflow or alert.workflow_filter not in workflow:
                return False

        if alert.service_filter:
            service = trace_data.get("service_name", "")
            if not service or alert.service_filter not in service:
                return False

        return True

    def _is_cooldown_expired(self, alert: Alert) -> bool:
        """Check if alert cooldown period has expired"""
        if not alert.last_triggered_at:
            return True

        cooldown_ms = alert.cooldown_minutes * 60 * 1000
        now_ms = int(datetime.now().timestamp() * 1000)

        return (now_ms - alert.last_triggered_at) >= cooldown_ms

    def _extract_value(self, condition_type: AlertConditionType, trace_data: dict) -> Optional[float]:
        """Extract value from trace data based on condition type"""
        if condition_type == AlertConditionType.DURATION_THRESHOLD:
            return trace_data.get("duration_ms")

        elif condition_type == AlertConditionType.ERROR_COUNT:
            return float(trace_data.get("error_count", 0))

        elif condition_type == AlertConditionType.ERROR_RATE:
            span_count = trace_data.get("span_count", 0)
            if span_count == 0:
                return 0.0
            error_count = trace_data.get("error_count", 0)
            return (error_count / span_count) * 100  # Percentage

        elif condition_type == AlertConditionType.COST_THRESHOLD:
            return trace_data.get("total_cost", 0.0)

        elif condition_type == AlertConditionType.SPAN_COUNT:
            return float(trace_data.get("span_count", 0))

        return None

    def _create_alert_event(self, alert: Alert, trace_data: dict, actual_value: float) -> AlertEvent:
        """Create an AlertEvent from triggered alert"""
        # Build message
        condition_desc = self._format_condition(alert.condition.condition_type, alert.condition.threshold)
        actual_desc = self._format_value(alert.condition.condition_type, actual_value)

        message = (
            f"Alert '{alert.name}' triggered: "
            f"{condition_desc}, actual: {actual_desc}"
        )

        return AlertEvent(
            id=str(uuid.uuid4()),
            alert_id=alert.id,
            alert_name=alert.name,
            severity=alert.severity,
            trace_id=trace_data["trace_id"],
            workflow_name=trace_data.get("workflow_name"),
            service_name=trace_data.get("service_name"),
            condition_type=alert.condition.condition_type,
            threshold=alert.condition.threshold,
            actual_value=actual_value,
            message=message
        )

    def _format_condition(self, condition_type: AlertConditionType, threshold: float) -> str:
        """Format condition for display"""
        if condition_type == AlertConditionType.DURATION_THRESHOLD:
            return f"duration > {threshold}ms"
        elif condition_type == AlertConditionType.ERROR_COUNT:
            return f"errors > {int(threshold)}"
        elif condition_type == AlertConditionType.ERROR_RATE:
            return f"error rate > {threshold}%"
        elif condition_type == AlertConditionType.COST_THRESHOLD:
            return f"cost > ${threshold:.6f}"
        elif condition_type == AlertConditionType.SPAN_COUNT:
            return f"spans > {int(threshold)}"
        return f"threshold > {threshold}"

    def _format_value(self, condition_type: AlertConditionType, value: float) -> str:
        """Format actual value for display"""
        if condition_type == AlertConditionType.DURATION_THRESHOLD:
            return f"{value}ms"
        elif condition_type == AlertConditionType.ERROR_COUNT:
            return str(int(value))
        elif condition_type == AlertConditionType.ERROR_RATE:
            return f"{value:.1f}%"
        elif condition_type == AlertConditionType.COST_THRESHOLD:
            return f"${value:.6f}"
        elif condition_type == AlertConditionType.SPAN_COUNT:
            return str(int(value))
        return str(value)
