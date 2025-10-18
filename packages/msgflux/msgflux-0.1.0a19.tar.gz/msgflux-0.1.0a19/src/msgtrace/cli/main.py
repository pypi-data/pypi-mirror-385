"""CLI for msgtrace."""

import sys
from typing import Optional

import click
import uvicorn

from msgtrace.backend.api.app import create_app
from msgtrace.core.config import MsgTraceConfig
from msgtrace.logger import logger


@click.group()
@click.version_option(version="0.1.0", prog_name="msgtrace")
def cli():
    """msgtrace - Trace visualization and observability for msgflux.

    A lightweight, self-hosted observability platform for msgflux AI systems.
    """
    pass


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind the server to",
    show_default=True,
)
@click.option(
    "--port",
    default=4321,
    help="Port to bind the server to",
    show_default=True,
)
@click.option(
    "--db-path",
    default="msgtrace.db",
    help="Path to SQLite database",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
def start(host: str, port: int, db_path: str, reload: bool):
    """Start the msgtrace server.

    The server will listen for OTLP traces and provide a REST API
    for querying and visualizing trace data.

    Example:
        msgtrace start --port 4321
    """
    logger.info("Starting msgtrace server...")
    logger.info(f"Database: {db_path}")
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"OTLP endpoint: http://{host}:{port}/api/v1/traces/export")
    logger.info(f"API docs: http://{host}:{port}/docs")

    config = MsgTraceConfig(host=host, port=port, db_path=db_path)

    if reload:
        # Development mode with auto-reload
        uvicorn.run(
            "msgtrace.backend.api.app:create_app",
            host=host,
            port=port,
            reload=True,
            factory=True,
        )
    else:
        # Production mode
        app = create_app(config)
        uvicorn.run(app, host=host, port=port)


@cli.command()
@click.option(
    "--db-path",
    default="msgtrace.db",
    help="Path to SQLite database",
    show_default=True,
)
def stats(db_path: str):
    """Display statistics about stored traces.

    Shows information about total traces, errors, and storage usage.

    Example:
        msgtrace stats
    """
    import asyncio
    from pathlib import Path

    from msgtrace.backend.storage.sqlite import SQLiteTraceStorage
    from msgtrace.core.models import TraceQueryParams

    async def get_stats():
        storage = SQLiteTraceStorage(db_path)

        all_params = TraceQueryParams(limit=1)
        total = await storage.count_traces(all_params)

        error_params = TraceQueryParams(has_errors=True, limit=1)
        errors = await storage.count_traces(error_params)

        await storage.close()

        return total, errors

    if not Path(db_path).exists():
        click.echo(f"Database not found: {db_path}")
        sys.exit(1)

    total, errors = asyncio.run(get_stats())

    click.echo("\n📊 msgtrace Statistics")
    click.echo("=" * 40)
    click.echo(f"Total traces: {total}")
    click.echo(f"Traces with errors: {errors}")
    if total > 0:
        error_rate = (errors / total) * 100
        click.echo(f"Error rate: {error_rate:.2f}%")
    click.echo(f"Database: {db_path}")

    # Get file size
    db_size = Path(db_path).stat().st_size
    db_size_mb = db_size / (1024 * 1024)
    click.echo(f"Database size: {db_size_mb:.2f} MB")
    click.echo()


@cli.command()
@click.option(
    "--db-path",
    default="msgtrace.db",
    help="Path to SQLite database",
    show_default=True,
)
@click.option(
    "--limit",
    default=10,
    help="Number of traces to list",
    show_default=True,
)
def list(db_path: str, limit: int):
    """List recent traces.

    Shows a summary of recent traces with basic information.

    Example:
        msgtrace list --limit 20
    """
    import asyncio
    from pathlib import Path

    from msgtrace.backend.storage.sqlite import SQLiteTraceStorage
    from msgtrace.core.models import TraceQueryParams

    async def list_traces():
        storage = SQLiteTraceStorage(db_path)
        params = TraceQueryParams(limit=limit)
        traces = await storage.list_traces(params)
        await storage.close()
        return traces

    if not Path(db_path).exists():
        click.echo(f"Database not found: {db_path}")
        sys.exit(1)

    traces = asyncio.run(list_traces())

    if not traces:
        click.echo("No traces found.")
        return

    click.echo(f"\n🔍 Recent Traces (showing {len(traces)} of {limit})")
    click.echo("=" * 80)

    for trace in traces:
        error_badge = "❌" if trace.error_count > 0 else "✅"
        click.echo(f"\n{error_badge} {trace.trace_id[:16]}...")
        click.echo(f"   Workflow: {trace.workflow_name or 'N/A'}")
        click.echo(f"   Duration: {trace.duration_ms:.2f}ms")
        click.echo(f"   Spans: {trace.span_count} | Errors: {trace.error_count}")

    click.echo()


@cli.command()
@click.argument("trace_id")
@click.option(
    "--db-path",
    default="msgtrace.db",
    help="Path to SQLite database",
    show_default=True,
)
def show(trace_id: str, db_path: str):
    """Show detailed information about a specific trace.

    Displays all spans and their attributes for a given trace ID.

    Example:
        msgtrace show abc123def456
    """
    import asyncio
    from pathlib import Path

    from msgtrace.backend.storage.sqlite import SQLiteTraceStorage

    async def get_trace(trace_id: str):
        storage = SQLiteTraceStorage(db_path)
        trace = await storage.get_trace(trace_id)
        await storage.close()
        return trace

    if not Path(db_path).exists():
        click.echo(f"Database not found: {db_path}")
        sys.exit(1)

    trace = asyncio.run(get_trace(trace_id))

    if not trace:
        click.echo(f"Trace not found: {trace_id}")
        sys.exit(1)

    click.echo(f"\n🔍 Trace: {trace.trace_id}")
    click.echo("=" * 80)
    click.echo(f"Workflow: {trace.workflow_name or 'N/A'}")
    click.echo(f"Service: {trace.service_name or 'N/A'}")
    click.echo(f"Duration: {trace.duration_ms:.2f}ms")
    click.echo(f"Spans: {trace.span_count}")
    click.echo(f"Errors: {trace.error_count}")

    click.echo(f"\n📋 Spans ({len(trace.spans)}):")
    click.echo("-" * 80)

    for span in trace.spans:
        indent = "  " * (0 if span.is_root() else 1)
        error_badge = "❌" if span.is_error() else "  "
        click.echo(f"{indent}{error_badge} {span.name}")
        click.echo(f"{indent}   ID: {span.span_id[:16]}...")
        click.echo(f"{indent}   Duration: {span.duration_ms:.2f}ms")
        if span.status and span.status.status_code == "ERROR":
            click.echo(f"{indent}   Error: {span.status.description}")

    click.echo()


@cli.command()
@click.option(
    "--db-path",
    default="msgtrace.db",
    help="Path to SQLite database",
    show_default=True,
)
@click.confirmation_option(prompt="Are you sure you want to clear all traces?")
def clear(db_path: str):
    """Clear all traces from the database.

    WARNING: This will delete all stored trace data!

    Example:
        msgtrace clear
    """
    from pathlib import Path

    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()
        click.echo(f"✅ Database cleared: {db_path}")
    else:
        click.echo(f"Database not found: {db_path}")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
