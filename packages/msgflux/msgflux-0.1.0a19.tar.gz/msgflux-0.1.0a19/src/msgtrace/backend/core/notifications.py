"""
Notification System for msgtrace Alerts

Handles delivery of alert notifications via multiple channels.
"""

import aiohttp
import asyncio
import json
from typing import Optional
from datetime import datetime

from .alert_models import AlertEvent, NotificationChannel, NotificationConfig


class NotificationService:
    """
    Service for sending alert notifications via various channels.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def send_notification(self, event: AlertEvent, config: NotificationConfig):
        """
        Send notification for an alert event.

        Args:
            event: The alert event to notify about
            config: Notification configuration
        """
        if not config.enabled:
            return

        try:
            if config.channel == NotificationChannel.WEBHOOK:
                await self._send_webhook(event, config)
            elif config.channel == NotificationChannel.CONSOLE:
                await self._send_console(event, config)
            elif config.channel == NotificationChannel.EMAIL:
                await self._send_email(event, config)
            elif config.channel == NotificationChannel.SLACK:
                await self._send_slack(event, config)
        except Exception as e:
            print(f"Error sending notification via {config.channel}: {e}")

    async def _send_webhook(self, event: AlertEvent, config: NotificationConfig):
        """Send webhook notification"""
        url = config.config.get("url")
        if not url:
            raise ValueError("Webhook URL not configured")

        headers = config.config.get("headers", {})
        headers.setdefault("Content-Type", "application/json")

        payload = self._build_webhook_payload(event, config)

        if not self.session:
            self.session = aiohttp.ClientSession()

        async with self.session.post(url, json=payload, headers=headers, timeout=10) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Webhook request failed: {response.status} - {error_text}")

    async def _send_console(self, event: AlertEvent, config: NotificationConfig):
        """Send console notification (for testing/debugging)"""
        severity_colors = {
            "info": "\033[94m",  # Blue
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "critical": "\033[95m",  # Magenta
        }
        reset = "\033[0m"

        color = severity_colors.get(event.severity.value, "")
        timestamp = datetime.fromtimestamp(event.triggered_at / 1000).strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{color}🚨 ALERT TRIGGERED {reset}")
        print(f"  Time: {timestamp}")
        print(f"  Severity: {color}{event.severity.value.upper()}{reset}")
        print(f"  Alert: {event.alert_name}")
        print(f"  Message: {event.message}")
        print(f"  Trace ID: {event.trace_id}")
        if event.workflow_name:
            print(f"  Workflow: {event.workflow_name}")
        if event.service_name:
            print(f"  Service: {event.service_name}")
        print(f"  Threshold: {event.threshold}")
        print(f"  Actual: {event.actual_value}")
        print(f"{color}{'─' * 60}{reset}\n")

    async def _send_email(self, event: AlertEvent, config: NotificationConfig):
        """Send email notification (placeholder for future implementation)"""
        # TODO: Implement email notifications using SMTP
        print(f"Email notification not yet implemented for alert: {event.alert_name}")
        pass

    async def _send_slack(self, event: AlertEvent, config: NotificationConfig):
        """Send Slack notification"""
        webhook_url = config.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("Slack webhook URL not configured")

        # Map severity to Slack colors
        severity_colors = {
            "info": "#36a64f",  # Green
            "warning": "#ff9800",  # Orange
            "error": "#f44336",  # Red
            "critical": "#9c27b0",  # Purple
        }

        color = severity_colors.get(event.severity.value, "#808080")

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 {event.alert_name}",
                    "text": event.message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": event.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Trace ID",
                            "value": event.trace_id[:16] + "...",
                            "short": True
                        },
                        {
                            "title": "Threshold",
                            "value": str(event.threshold),
                            "short": True
                        },
                        {
                            "title": "Actual Value",
                            "value": str(event.actual_value),
                            "short": True
                        }
                    ],
                    "footer": "msgtrace Alert System",
                    "ts": int(event.triggered_at / 1000)
                }
            ]
        }

        if event.workflow_name:
            payload["attachments"][0]["fields"].append({
                "title": "Workflow",
                "value": event.workflow_name,
                "short": True
            })

        if event.service_name:
            payload["attachments"][0]["fields"].append({
                "title": "Service",
                "value": event.service_name,
                "short": True
            })

        if not self.session:
            self.session = aiohttp.ClientSession()

        async with self.session.post(webhook_url, json=payload, timeout=10) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Slack webhook failed: {response.status} - {error_text}")

    def _build_webhook_payload(self, event: AlertEvent, config: NotificationConfig) -> dict:
        """Build webhook payload"""
        # Base payload
        payload = {
            "event_id": event.id,
            "alert_id": event.alert_id,
            "alert_name": event.alert_name,
            "severity": event.severity.value,
            "message": event.message,
            "trace_id": event.trace_id,
            "condition_type": event.condition_type.value,
            "threshold": event.threshold,
            "actual_value": event.actual_value,
            "triggered_at": event.triggered_at,
            "triggered_at_iso": datetime.fromtimestamp(event.triggered_at / 1000).isoformat()
        }

        # Add optional fields
        if event.workflow_name:
            payload["workflow_name"] = event.workflow_name

        if event.service_name:
            payload["service_name"] = event.service_name

        # Allow custom payload template
        template = config.config.get("payload_template")
        if template:
            # Simple template substitution
            custom_payload = json.loads(template)
            # Merge custom with base
            return {**payload, **custom_payload}

        return payload

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
