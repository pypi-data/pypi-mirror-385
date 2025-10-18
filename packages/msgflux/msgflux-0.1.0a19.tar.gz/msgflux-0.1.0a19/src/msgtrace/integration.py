"""Integration helpers for msgflux."""

from typing import Optional

from msgtrace.core.client import MsgTraceServer, start_observer
from msgtrace.logger import logger


def configure_msgflux_telemetry(
    server: Optional[MsgTraceServer] = None,
    host: str = "localhost",
    port: int = 4321,
    enable_state_dict: bool = False,
    enable_platform: bool = False,
    enable_tool_responses: bool = True,
    enable_agent_state: bool = False,
) -> None:
    """Configure msgflux to send traces to msgtrace.

    This is a convenience function that automatically configures msgflux
    environment variables to work with msgtrace.

    Args:
        server: Optional MsgTraceServer instance (for validation)
        host: Hostname where msgtrace is running
        port: Port where msgtrace is running
        enable_state_dict: Capture module state dicts in traces
        enable_platform: Capture platform information
        enable_tool_responses: Capture tool call responses
        enable_agent_state: Capture agent state and tool schemas

    Example:
        ```python
        from msgtrace import start_observer, configure_msgflux_telemetry

        # Start the observer
        observer = start_observer(port=4321)

        # Configure msgflux
        configure_msgflux_telemetry(
            server=observer,
            enable_state_dict=True,
        )

        # Now your msgflux code will send traces to msgtrace
        ```
    """
    try:
        from msgflux.envs import set_envs
    except ImportError:
        logger.error("msgflux is not installed. Please install msgflux first.")
        return

    endpoint = f"http://{host}:{port}/api/v1/traces/export"

    logger.info(f"Configuring msgflux telemetry to send to: {endpoint}")

    set_envs(
        telemetry_requires_trace=True,
        telemetry_span_exporter_type="otlp",
        telemetry_otlp_endpoint=endpoint,
        telemetry_capture_state_dict=enable_state_dict,
        telemetry_capture_platform=enable_platform,
        telemetry_capture_tool_call_responses=enable_tool_responses,
        telemetry_capture_agent_prepare_model_execution=enable_agent_state,
    )

    logger.info("✅ msgflux telemetry configured successfully")


def quick_start(
    port: int = 4321,
    db_path: str = "msgtrace.db",
    enable_state_dict: bool = False,
    enable_platform: bool = False,
) -> MsgTraceServer:
    """Quick start msgtrace with automatic msgflux configuration.

    This is the easiest way to get started with msgtrace. It starts
    the server and configures msgflux in one call.

    Args:
        port: Port to run msgtrace server on
        db_path: Path to SQLite database
        enable_state_dict: Capture module state dicts
        enable_platform: Capture platform information

    Returns:
        MsgTraceServer instance

    Example:
        ```python
        from msgtrace.integration import quick_start

        # Start and configure everything
        observer = quick_start(port=4321)

        # Your msgflux code here
        # ...

        # Stop when done
        observer.stop()
        ```
    """
    logger.info("🚀 Quick starting msgtrace...")

    # Start the server
    server = start_observer(port=port, db_path=db_path)

    # Configure msgflux
    configure_msgflux_telemetry(
        server=server,
        port=port,
        enable_state_dict=enable_state_dict,
        enable_platform=enable_platform,
    )

    logger.info(f"✅ msgtrace is ready!")
    logger.info(f"   Server: http://localhost:{port}")
    logger.info(f"   API Docs: http://localhost:{port}/docs")

    return server
