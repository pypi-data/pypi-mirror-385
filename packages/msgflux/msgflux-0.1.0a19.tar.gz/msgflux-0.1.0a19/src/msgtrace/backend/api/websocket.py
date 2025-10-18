"""WebSocket support for real-time trace updates."""

import asyncio
import json
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect
from msgspec import to_builtins


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.discard(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client.

        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast
        """
        # Convert msgspec objects to dict
        if hasattr(message, "__struct_fields__"):
            message = to_builtins(message)

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_trace_created(self, trace_summary):
        """Broadcast when a new trace is created.

        Args:
            trace_summary: TraceSummary object
        """
        await self.broadcast({
            "type": "trace_created",
            "data": to_builtins(trace_summary),
        })

    async def broadcast_trace_updated(self, trace_summary):
        """Broadcast when a trace is updated.

        Args:
            trace_summary: TraceSummary object
        """
        await self.broadcast({
            "type": "trace_updated",
            "data": to_builtins(trace_summary),
        })

    async def broadcast_trace_deleted(self, trace_id: str):
        """Broadcast when a trace is deleted.

        Args:
            trace_id: ID of deleted trace
        """
        await self.broadcast({
            "type": "trace_deleted",
            "data": {"trace_id": trace_id},
        })

    async def broadcast_stats_updated(self, stats: dict):
        """Broadcast when stats are updated.

        Args:
            stats: Statistics dictionary
        """
        await self.broadcast({
            "type": "stats_updated",
            "data": stats,
        })

    async def broadcast_alert_triggered(self, alert_event):
        """Broadcast when an alert is triggered.

        Args:
            alert_event: AlertEvent object
        """
        await self.broadcast({
            "type": "alert_triggered",
            "data": {
                "id": alert_event.id,
                "alert_id": alert_event.alert_id,
                "alert_name": alert_event.alert_name,
                "severity": alert_event.severity.value,
                "trace_id": alert_event.trace_id,
                "workflow_name": alert_event.workflow_name,
                "service_name": alert_event.service_name,
                "condition_type": alert_event.condition_type.value,
                "threshold": alert_event.threshold,
                "actual_value": alert_event.actual_value,
                "message": alert_event.message,
                "triggered_at": alert_event.triggered_at,
            },
        })

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
