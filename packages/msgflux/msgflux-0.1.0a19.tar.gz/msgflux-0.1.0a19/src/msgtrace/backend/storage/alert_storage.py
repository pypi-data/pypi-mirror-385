"""
Alert Storage for msgtrace

Manages alert configurations and alert events in SQLite.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from ..core.alert_models import (
    Alert,
    AlertEvent,
    AlertCondition,
    NotificationConfig,
    AlertConditionType,
    AlertOperator,
    AlertSeverity,
    NotificationChannel,
    AlertStats,
)


class AlertStorage:
    """Storage for alerts and alert events"""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    condition_type TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    condition_field TEXT,
                    severity TEXT NOT NULL,
                    notifications TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    cooldown_minutes INTEGER NOT NULL DEFAULT 5,
                    workflow_filter TEXT,
                    service_filter TEXT,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    last_triggered_at INTEGER,
                    trigger_count INTEGER NOT NULL DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS alert_events (
                    id TEXT PRIMARY KEY,
                    alert_id TEXT NOT NULL,
                    alert_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    workflow_name TEXT,
                    service_name TEXT,
                    condition_type TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    actual_value REAL NOT NULL,
                    message TEXT NOT NULL,
                    triggered_at INTEGER NOT NULL,
                    acknowledged INTEGER NOT NULL DEFAULT 0,
                    acknowledged_at INTEGER,
                    acknowledged_by TEXT,
                    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_enabled ON alerts(enabled)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alert_events_alert_id ON alert_events(alert_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alert_events_triggered_at ON alert_events(triggered_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alert_events_severity ON alert_events(severity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alert_events_acknowledged ON alert_events(acknowledged)")

            conn.commit()

    def create_alert(self, alert: Alert) -> Alert:
        """Create a new alert"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alerts (
                    id, name, description, condition_type, operator, threshold, condition_field,
                    severity, notifications, enabled, cooldown_minutes, workflow_filter, service_filter,
                    created_at, updated_at, last_triggered_at, trigger_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.name,
                alert.description,
                alert.condition.condition_type.value,
                alert.condition.operator.value,
                alert.condition.threshold,
                alert.condition.field,
                alert.severity.value,
                json.dumps([{
                    "channel": n.channel.value,
                    "config": n.config,
                    "enabled": n.enabled
                } for n in alert.notifications]),
                1 if alert.enabled else 0,
                alert.cooldown_minutes,
                alert.workflow_filter,
                alert.service_filter,
                alert.created_at,
                alert.updated_at,
                alert.last_triggered_at,
                alert.trigger_count
            ))
            conn.commit()

        return alert

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_alert(row)

    def list_alerts(self, enabled_only: bool = False) -> list[Alert]:
        """List all alerts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM alerts"
            if enabled_only:
                query += " WHERE enabled = 1"
            query += " ORDER BY created_at DESC"

            cursor = conn.execute(query)
            return [self._row_to_alert(row) for row in cursor.fetchall()]

    def update_alert(self, alert: Alert) -> Alert:
        """Update an existing alert"""
        alert.updated_at = int(datetime.now().timestamp() * 1000)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE alerts SET
                    name = ?, description = ?, condition_type = ?, operator = ?, threshold = ?,
                    condition_field = ?, severity = ?, notifications = ?, enabled = ?,
                    cooldown_minutes = ?, workflow_filter = ?, service_filter = ?, updated_at = ?,
                    last_triggered_at = ?, trigger_count = ?
                WHERE id = ?
            """, (
                alert.name,
                alert.description,
                alert.condition.condition_type.value,
                alert.condition.operator.value,
                alert.condition.threshold,
                alert.condition.field,
                alert.severity.value,
                json.dumps([{
                    "channel": n.channel.value,
                    "config": n.config,
                    "enabled": n.enabled
                } for n in alert.notifications]),
                1 if alert.enabled else 0,
                alert.cooldown_minutes,
                alert.workflow_filter,
                alert.service_filter,
                alert.updated_at,
                alert.last_triggered_at,
                alert.trigger_count,
                alert.id
            ))
            conn.commit()

        return alert

    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            conn.commit()
            return cursor.rowcount > 0

    def create_alert_event(self, event: AlertEvent) -> AlertEvent:
        """Create a new alert event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alert_events (
                    id, alert_id, alert_name, severity, trace_id, workflow_name, service_name,
                    condition_type, threshold, actual_value, message, triggered_at,
                    acknowledged, acknowledged_at, acknowledged_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.alert_id,
                event.alert_name,
                event.severity.value,
                event.trace_id,
                event.workflow_name,
                event.service_name,
                event.condition_type.value,
                event.threshold,
                event.actual_value,
                event.message,
                event.triggered_at,
                1 if event.acknowledged else 0,
                event.acknowledged_at,
                event.acknowledged_by
            ))
            conn.commit()

        return event

    def list_alert_events(
        self,
        alert_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None
    ) -> list[AlertEvent]:
        """List alert events with filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = "SELECT * FROM alert_events WHERE 1=1"
            params = []

            if alert_id:
                query += " AND alert_id = ?"
                params.append(alert_id)

            if severity:
                query += " AND severity = ?"
                params.append(severity)

            if acknowledged is not None:
                query += " AND acknowledged = ?"
                params.append(1 if acknowledged else 0)

            query += " ORDER BY triggered_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(query, params)
            return [self._row_to_alert_event(row) for row in cursor.fetchall()]

    def acknowledge_event(self, event_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE alert_events SET
                    acknowledged = 1,
                    acknowledged_at = ?,
                    acknowledged_by = ?
                WHERE id = ?
            """, (int(datetime.now().timestamp() * 1000), acknowledged_by, event_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_alert_stats(self) -> AlertStats:
        """Get alert statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Total alerts
            cursor = conn.execute("SELECT COUNT(*) FROM alerts")
            total_alerts = cursor.fetchone()[0]

            # Enabled alerts
            cursor = conn.execute("SELECT COUNT(*) FROM alerts WHERE enabled = 1")
            enabled_alerts = cursor.fetchone()[0]

            # Total events
            cursor = conn.execute("SELECT COUNT(*) FROM alert_events")
            total_events = cursor.fetchone()[0]

            # Events last 24h
            yesterday = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
            cursor = conn.execute(
                "SELECT COUNT(*) FROM alert_events WHERE triggered_at >= ?",
                (yesterday,)
            )
            events_last_24h = cursor.fetchone()[0]

            # Events by severity
            cursor = conn.execute("""
                SELECT severity, COUNT(*) as count
                FROM alert_events
                GROUP BY severity
            """)
            events_by_severity = {row[0]: row[1] for row in cursor.fetchall()}

            # Most triggered alert
            cursor = conn.execute("""
                SELECT alert_name, COUNT(*) as count
                FROM alert_events
                GROUP BY alert_id, alert_name
                ORDER BY count DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            most_triggered = (row[0], row[1]) if row else None

            return AlertStats(
                total_alerts=total_alerts,
                enabled_alerts=enabled_alerts,
                total_events=total_events,
                events_last_24h=events_last_24h,
                events_by_severity=events_by_severity,
                most_triggered_alert=most_triggered
            )

    def _row_to_alert(self, row: sqlite3.Row) -> Alert:
        """Convert database row to Alert object"""
        notifications_data = json.loads(row["notifications"])
        notifications = [
            NotificationConfig(
                channel=NotificationChannel(n["channel"]),
                config=n["config"],
                enabled=n["enabled"]
            )
            for n in notifications_data
        ]

        condition = AlertCondition(
            condition_type=AlertConditionType(row["condition_type"]),
            operator=AlertOperator(row["operator"]),
            threshold=row["threshold"],
            field=row["condition_field"]
        )

        return Alert(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            condition=condition,
            severity=AlertSeverity(row["severity"]),
            notifications=notifications,
            enabled=bool(row["enabled"]),
            cooldown_minutes=row["cooldown_minutes"],
            workflow_filter=row["workflow_filter"],
            service_filter=row["service_filter"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_triggered_at=row["last_triggered_at"],
            trigger_count=row["trigger_count"]
        )

    def _row_to_alert_event(self, row: sqlite3.Row) -> AlertEvent:
        """Convert database row to AlertEvent object"""
        return AlertEvent(
            id=row["id"],
            alert_id=row["alert_id"],
            alert_name=row["alert_name"],
            severity=AlertSeverity(row["severity"]),
            trace_id=row["trace_id"],
            workflow_name=row["workflow_name"],
            service_name=row["service_name"],
            condition_type=AlertConditionType(row["condition_type"]),
            threshold=row["threshold"],
            actual_value=row["actual_value"],
            message=row["message"],
            triggered_at=row["triggered_at"],
            acknowledged=bool(row["acknowledged"]),
            acknowledged_at=row["acknowledged_at"],
            acknowledged_by=row["acknowledged_by"]
        )
