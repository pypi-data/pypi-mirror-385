"""
Alert Models for msgtrace Alerting System

Defines alert configurations, conditions, and notification settings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime


class AlertConditionType(str, Enum):
    """Types of alert conditions"""
    DURATION_THRESHOLD = "duration_threshold"
    ERROR_RATE = "error_rate"
    COST_THRESHOLD = "cost_threshold"
    SPAN_COUNT = "span_count"
    ERROR_COUNT = "error_count"


class AlertOperator(str, Enum):
    """Comparison operators for alert conditions"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN_OR_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "neq"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    CONSOLE = "console"  # For testing/debugging


@dataclass
class AlertCondition:
    """Defines a condition that triggers an alert"""
    condition_type: AlertConditionType
    operator: AlertOperator
    threshold: float
    field: Optional[str] = None  # For custom fields

    def evaluate(self, value: float) -> bool:
        """Evaluate if the condition is met"""
        if self.operator == AlertOperator.GREATER_THAN:
            return value > self.threshold
        elif self.operator == AlertOperator.LESS_THAN:
            return value < self.threshold
        elif self.operator == AlertOperator.GREATER_THAN_OR_EQUAL:
            return value >= self.threshold
        elif self.operator == AlertOperator.LESS_THAN_OR_EQUAL:
            return value <= self.threshold
        elif self.operator == AlertOperator.EQUAL:
            return value == self.threshold
        elif self.operator == AlertOperator.NOT_EQUAL:
            return value != self.threshold
        return False


@dataclass
class NotificationConfig:
    """Configuration for alert notifications"""
    channel: NotificationChannel
    config: dict[str, Any]  # Channel-specific config (webhook URL, email, etc.)
    enabled: bool = True


@dataclass
class Alert:
    """Alert configuration"""
    id: str
    name: str
    description: Optional[str]
    condition: AlertCondition
    severity: AlertSeverity
    notifications: list[NotificationConfig]
    enabled: bool = True
    cooldown_minutes: int = 5  # Minimum time between alerts
    workflow_filter: Optional[str] = None  # Filter by workflow name
    service_filter: Optional[str] = None  # Filter by service name
    created_at: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    updated_at: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    last_triggered_at: Optional[int] = None
    trigger_count: int = 0


@dataclass
class AlertEvent:
    """Represents a triggered alert event"""
    id: str
    alert_id: str
    alert_name: str
    severity: AlertSeverity
    trace_id: str
    workflow_name: Optional[str]
    service_name: Optional[str]
    condition_type: AlertConditionType
    threshold: float
    actual_value: float
    message: str
    triggered_at: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    acknowledged: bool = False
    acknowledged_at: Optional[int] = None
    acknowledged_by: Optional[str] = None


@dataclass
class AlertStats:
    """Statistics about alerts"""
    total_alerts: int
    enabled_alerts: int
    total_events: int
    events_last_24h: int
    events_by_severity: dict[str, int]
    most_triggered_alert: Optional[tuple[str, int]]  # (alert_name, count)
