"""
Alert REST API endpoints
"""

import uuid
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from ...core.alert_models import (
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
from ...storage.alert_storage import AlertStorage


router = APIRouter(prefix="/alerts", tags=["alerts"])


# Request/Response Models
class AlertConditionRequest(BaseModel):
    condition_type: str
    operator: str
    threshold: float
    field: Optional[str] = None


class NotificationConfigRequest(BaseModel):
    channel: str
    config: dict
    enabled: bool = True


class CreateAlertRequest(BaseModel):
    name: str
    description: Optional[str] = None
    condition: AlertConditionRequest
    severity: str
    notifications: list[NotificationConfigRequest]
    enabled: bool = True
    cooldown_minutes: int = 5
    workflow_filter: Optional[str] = None
    service_filter: Optional[str] = None


class UpdateAlertRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[AlertConditionRequest] = None
    severity: Optional[str] = None
    notifications: Optional[list[NotificationConfigRequest]] = None
    enabled: Optional[bool] = None
    cooldown_minutes: Optional[int] = None
    workflow_filter: Optional[str] = None
    service_filter: Optional[str] = None


class AcknowledgeEventRequest(BaseModel):
    acknowledged_by: str


# Dependency to get alert storage
def get_alert_storage():
    """Get alert storage instance - will be injected by app"""
    # This will be set by the main app
    return None


# Endpoints
@router.post("", status_code=201)
async def create_alert(request: CreateAlertRequest):
    """Create a new alert"""
    storage: AlertStorage = get_alert_storage()

    try:
        condition = AlertCondition(
            condition_type=AlertConditionType(request.condition.condition_type),
            operator=AlertOperator(request.condition.operator),
            threshold=request.condition.threshold,
            field=request.condition.field
        )

        notifications = [
            NotificationConfig(
                channel=NotificationChannel(n.channel),
                config=n.config,
                enabled=n.enabled
            )
            for n in request.notifications
        ]

        alert = Alert(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            condition=condition,
            severity=AlertSeverity(request.severity),
            notifications=notifications,
            enabled=request.enabled,
            cooldown_minutes=request.cooldown_minutes,
            workflow_filter=request.workflow_filter,
            service_filter=request.service_filter
        )

        created_alert = storage.create_alert(alert)

        return {
            "id": created_alert.id,
            "name": created_alert.name,
            "description": created_alert.description,
            "condition": {
                "condition_type": created_alert.condition.condition_type.value,
                "operator": created_alert.condition.operator.value,
                "threshold": created_alert.condition.threshold,
                "field": created_alert.condition.field
            },
            "severity": created_alert.severity.value,
            "notifications": [
                {
                    "channel": n.channel.value,
                    "config": n.config,
                    "enabled": n.enabled
                }
                for n in created_alert.notifications
            ],
            "enabled": created_alert.enabled,
            "cooldown_minutes": created_alert.cooldown_minutes,
            "workflow_filter": created_alert.workflow_filter,
            "service_filter": created_alert.service_filter,
            "created_at": created_alert.created_at,
            "updated_at": created_alert.updated_at,
            "trigger_count": created_alert.trigger_count
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_alerts(enabled_only: bool = Query(False, description="Show only enabled alerts")):
    """List all alerts"""
    storage: AlertStorage = get_alert_storage()
    alerts = storage.list_alerts(enabled_only=enabled_only)

    return {
        "alerts": [
            {
                "id": alert.id,
                "name": alert.name,
                "description": alert.description,
                "condition": {
                    "condition_type": alert.condition.condition_type.value,
                    "operator": alert.condition.operator.value,
                    "threshold": alert.condition.threshold,
                    "field": alert.condition.field
                },
                "severity": alert.severity.value,
                "notifications": [
                    {
                        "channel": n.channel.value,
                        "config": n.config,
                        "enabled": n.enabled
                    }
                    for n in alert.notifications
                ],
                "enabled": alert.enabled,
                "cooldown_minutes": alert.cooldown_minutes,
                "workflow_filter": alert.workflow_filter,
                "service_filter": alert.service_filter,
                "created_at": alert.created_at,
                "updated_at": alert.updated_at,
                "last_triggered_at": alert.last_triggered_at,
                "trigger_count": alert.trigger_count
            }
            for alert in alerts
        ],
        "total": len(alerts)
    }


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get alert by ID"""
    storage: AlertStorage = get_alert_storage()
    alert = storage.get_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "id": alert.id,
        "name": alert.name,
        "description": alert.description,
        "condition": {
            "condition_type": alert.condition.condition_type.value,
            "operator": alert.condition.operator.value,
            "threshold": alert.condition.threshold,
            "field": alert.condition.field
        },
        "severity": alert.severity.value,
        "notifications": [
            {
                "channel": n.channel.value,
                "config": n.config,
                "enabled": n.enabled
            }
            for n in alert.notifications
        ],
        "enabled": alert.enabled,
        "cooldown_minutes": alert.cooldown_minutes,
        "workflow_filter": alert.workflow_filter,
        "service_filter": alert.service_filter,
        "created_at": alert.created_at,
        "updated_at": alert.updated_at,
        "last_triggered_at": alert.last_triggered_at,
        "trigger_count": alert.trigger_count
    }


@router.patch("/{alert_id}")
async def update_alert(alert_id: str, request: UpdateAlertRequest):
    """Update an alert"""
    storage: AlertStorage = get_alert_storage()
    alert = storage.get_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update fields
    if request.name is not None:
        alert.name = request.name
    if request.description is not None:
        alert.description = request.description
    if request.severity is not None:
        alert.severity = AlertSeverity(request.severity)
    if request.enabled is not None:
        alert.enabled = request.enabled
    if request.cooldown_minutes is not None:
        alert.cooldown_minutes = request.cooldown_minutes
    if request.workflow_filter is not None:
        alert.workflow_filter = request.workflow_filter
    if request.service_filter is not None:
        alert.service_filter = request.service_filter

    if request.condition is not None:
        alert.condition = AlertCondition(
            condition_type=AlertConditionType(request.condition.condition_type),
            operator=AlertOperator(request.condition.operator),
            threshold=request.condition.threshold,
            field=request.condition.field
        )

    if request.notifications is not None:
        alert.notifications = [
            NotificationConfig(
                channel=NotificationChannel(n.channel),
                config=n.config,
                enabled=n.enabled
            )
            for n in request.notifications
        ]

    updated_alert = storage.update_alert(alert)

    return {
        "id": updated_alert.id,
        "name": updated_alert.name,
        "description": updated_alert.description,
        "condition": {
            "condition_type": updated_alert.condition.condition_type.value,
            "operator": updated_alert.condition.operator.value,
            "threshold": updated_alert.condition.threshold,
            "field": updated_alert.condition.field
        },
        "severity": updated_alert.severity.value,
        "notifications": [
            {
                "channel": n.channel.value,
                "config": n.config,
                "enabled": n.enabled
            }
            for n in updated_alert.notifications
        ],
        "enabled": updated_alert.enabled,
        "cooldown_minutes": updated_alert.cooldown_minutes,
        "workflow_filter": updated_alert.workflow_filter,
        "service_filter": updated_alert.service_filter,
        "created_at": updated_alert.created_at,
        "updated_at": updated_alert.updated_at,
        "last_triggered_at": updated_alert.last_triggered_at,
        "trigger_count": updated_alert.trigger_count
    }


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    storage: AlertStorage = get_alert_storage()

    if not storage.delete_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"message": "Alert deleted successfully"}


@router.get("/events/list")
async def list_alert_events(
    alert_id: Optional[str] = Query(None, description="Filter by alert ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status")
):
    """List alert events"""
    storage: AlertStorage = get_alert_storage()
    events = storage.list_alert_events(
        alert_id=alert_id,
        limit=limit,
        offset=offset,
        severity=severity,
        acknowledged=acknowledged
    )

    return {
        "events": [
            {
                "id": event.id,
                "alert_id": event.alert_id,
                "alert_name": event.alert_name,
                "severity": event.severity.value,
                "trace_id": event.trace_id,
                "workflow_name": event.workflow_name,
                "service_name": event.service_name,
                "condition_type": event.condition_type.value,
                "threshold": event.threshold,
                "actual_value": event.actual_value,
                "message": event.message,
                "triggered_at": event.triggered_at,
                "acknowledged": event.acknowledged,
                "acknowledged_at": event.acknowledged_at,
                "acknowledged_by": event.acknowledged_by
            }
            for event in events
        ],
        "total": len(events),
        "limit": limit,
        "offset": offset
    }


@router.post("/events/{event_id}/acknowledge")
async def acknowledge_event(event_id: str, request: AcknowledgeEventRequest):
    """Acknowledge an alert event"""
    storage: AlertStorage = get_alert_storage()

    if not storage.acknowledge_event(event_id, request.acknowledged_by):
        raise HTTPException(status_code=404, detail="Alert event not found")

    return {"message": "Alert event acknowledged"}


@router.get("/stats")
async def get_alert_stats():
    """Get alert statistics"""
    storage: AlertStorage = get_alert_storage()
    stats = storage.get_alert_stats()

    return {
        "total_alerts": stats.total_alerts,
        "enabled_alerts": stats.enabled_alerts,
        "total_events": stats.total_events,
        "events_last_24h": stats.events_last_24h,
        "events_by_severity": stats.events_by_severity,
        "most_triggered_alert": {
            "name": stats.most_triggered_alert[0],
            "count": stats.most_triggered_alert[1]
        } if stats.most_triggered_alert else None
    }
