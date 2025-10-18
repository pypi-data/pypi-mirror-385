"""FastAPI application for msgtrace."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from msgtrace.backend.api.routes import traces, websocket, alerts, analytics
from msgtrace.backend.api.websocket import ConnectionManager
from msgtrace.backend.collectors.otlp import OTLPCollector
from msgtrace.backend.storage.sqlite import SQLiteTraceStorage
from msgtrace.backend.storage.alert_storage import AlertStorage
from msgtrace.backend.core.alert_engine import AlertEngine
from msgtrace.backend.core.notifications import NotificationService
from msgtrace.core.config import MsgTraceConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    storage = app.state.storage
    collector = app.state.collector
    notification_service = app.state.notification_service
    await collector.start()
    yield
    # Shutdown
    await collector.stop()
    await storage.close()
    await notification_service.close()


def create_app(config: Optional[MsgTraceConfig] = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        config: MsgTrace configuration

    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = MsgTraceConfig()

    app = FastAPI(
        title="msgtrace",
        description="Trace visualization and observability for msgflux",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize storage and collector
    storage = SQLiteTraceStorage(db_path=config.db_path)
    alert_storage = AlertStorage(db_path=config.db_path)
    ws_manager = ConnectionManager()

    # Initialize notification service and alert engine
    notification_service = NotificationService()

    async def on_alert_triggered(alert_event):
        """Handle triggered alerts."""
        # Send notifications
        alert = alert_storage.get_alert(alert_event.alert_id)
        if alert:
            for notification_config in alert.notifications:
                try:
                    await notification_service.send_notification(alert_event, notification_config)
                except Exception as e:
                    print(f"Error sending notification: {e}")

        # Broadcast to WebSocket clients
        try:
            await ws_manager.broadcast_alert_triggered(alert_event)
        except Exception as e:
            print(f"Error broadcasting alert: {e}")

    alert_engine = AlertEngine(
        storage=alert_storage,
        on_alert_triggered=on_alert_triggered
    )

    # Callback for trace notifications
    async def on_trace_received(trace_ids: list):
        """Notify WebSocket clients when traces are received."""
        from msgtrace.core.models import TraceQueryParams

        for trace_id in trace_ids:
            try:
                # Get trace summary
                traces = await storage.list_traces(
                    TraceQueryParams(limit=1, offset=0)
                )
                if traces:
                    # Find the matching trace (it should be recent)
                    matching = [t for t in traces if t.trace_id == trace_id]
                    if matching:
                        trace_summary = matching[0]
                        await ws_manager.broadcast_trace_created(trace_summary)

                        # Evaluate alerts for this trace
                        trace_data = {
                            "trace_id": trace_summary.trace_id,
                            "workflow_name": trace_summary.workflow_name,
                            "service_name": trace_summary.service_name,
                            "duration_ms": trace_summary.duration_ms,
                            "span_count": trace_summary.span_count,
                            "error_count": trace_summary.error_count,
                            "total_cost": 0.0  # TODO: Add cost calculation
                        }
                        await alert_engine.evaluate_trace(trace_data)
            except Exception as e:
                print(f"Error processing trace: {e}")

    collector = OTLPCollector(storage, on_trace_received=on_trace_received)

    # Store in app state
    app.state.storage = storage
    app.state.alert_storage = alert_storage
    app.state.alert_engine = alert_engine
    app.state.notification_service = notification_service
    app.state.collector = collector
    app.state.config = config
    app.state.ws_manager = ws_manager

    # Setup dependency injection for alert storage
    def get_alert_storage_override():
        return alert_storage

    alerts.get_alert_storage = get_alert_storage_override

    # Setup dependency injection for analytics
    def get_trace_storage_override():
        return storage

    analytics.get_trace_storage = get_trace_storage_override

    # Include routers
    app.include_router(traces.router, prefix="/api/v1")
    app.include_router(websocket.router, prefix="/api/v1")
    app.include_router(alerts.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    # Mount frontend static files (if available)
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists() and frontend_dist.is_dir():
        app.mount(
            "/",
            StaticFiles(directory=str(frontend_dist), html=True),
            name="frontend",
        )

    return app
