"""Client utilities for starting and managing msgtrace server."""

import asyncio
import threading
from typing import Optional

import uvicorn

from msgtrace.backend.api.app import create_app
from msgtrace.core.config import MsgTraceConfig
from msgtrace.logger import logger


class MsgTraceServer:
    """Wrapper for msgtrace server that can run in background."""

    def __init__(self, config: Optional[MsgTraceConfig] = None):
        """Initialize server.

        Args:
            config: Server configuration
        """
        self.config = config or MsgTraceConfig()
        self._server_thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        """Start the server in a background thread."""
        if self._running:
            logger.warning("Server is already running")
            return

        self._running = True
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()

        logger.info(
            f"msgtrace server starting on http://{self.config.host}:{self.config.port}"
        )
        logger.info(f"OTLP endpoint: http://{self.config.host}:{self.config.port}/api/v1/traces/export")

    def _run_server(self) -> None:
        """Run the server (internal method for thread)."""
        app = create_app(self.config)

        config = uvicorn.Config(
            app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
        )
        server = uvicorn.Server(config)

        # Run in new event loop for the thread
        asyncio.run(server.serve())

    def stop(self) -> None:
        """Stop the server."""
        if not self._running:
            return

        self._running = False
        logger.info("msgtrace server stopped")


def start_observer(
    host: str = "0.0.0.0",
    port: int = 4321,
    db_path: str = "msgtrace.db",
) -> MsgTraceServer:
    """Start msgtrace observer server.

    This is the main entry point for starting the msgtrace server
    from Python code. The server runs in a background thread.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        db_path: Path to SQLite database

    Returns:
        MsgTraceServer instance

    Example:
        ```python
        from msgtrace import start_observer
        from msgflux import set_envs

        # Start the observer
        observer = start_observer(port=4321)

        # Configure msgflux to send traces
        set_envs(
            telemetry_requires_trace=True,
            telemetry_span_exporter_type="otlp",
            telemetry_otlp_endpoint="http://localhost:4321/api/v1/traces/export",
        )

        # Your msgflux code here
        # ...

        # Stop the observer when done
        observer.stop()
        ```
    """
    config = MsgTraceConfig(host=host, port=port, db_path=db_path)
    server = MsgTraceServer(config)
    server.start()
    return server
