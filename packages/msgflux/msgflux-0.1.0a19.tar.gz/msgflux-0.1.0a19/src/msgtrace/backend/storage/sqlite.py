"""SQLite storage implementation for traces."""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import msgspec

from msgtrace.backend.storage.base import TraceStorage
from msgtrace.core.models import (
    Span,
    SpanEvent,
    SpanStatus,
    Trace,
    TraceQueryParams,
    TraceSummary,
)


class SQLiteTraceStorage(TraceStorage):
    """SQLite-based storage for traces and spans."""

    def __init__(self, db_path: str = "msgtrace.db"):
        """Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()
        self._encoder = msgspec.json.Encoder()
        self._decoder = msgspec.json.Decoder()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path, check_same_thread=False, timeout=10.0
            )
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS traces (
                trace_id TEXT PRIMARY KEY,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                root_span_id TEXT,
                service_name TEXT,
                workflow_name TEXT,
                span_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_traces_start_time
                ON traces(start_time DESC);
            CREATE INDEX IF NOT EXISTS idx_traces_service_name
                ON traces(service_name);
            CREATE INDEX IF NOT EXISTS idx_traces_workflow_name
                ON traces(workflow_name);
            CREATE INDEX IF NOT EXISTS idx_traces_duration
                ON traces(duration_ms);

            CREATE TABLE IF NOT EXISTS spans (
                span_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                parent_span_id TEXT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                attributes TEXT,
                events TEXT,
                status_code TEXT,
                status_description TEXT,
                resource_attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_spans_trace_id
                ON spans(trace_id);
            CREATE INDEX IF NOT EXISTS idx_spans_parent_span_id
                ON spans(parent_span_id);
            CREATE INDEX IF NOT EXISTS idx_spans_start_time
                ON spans(start_time DESC);
            CREATE INDEX IF NOT EXISTS idx_spans_name
                ON spans(name);
        """
        )
        conn.commit()

    async def save_span(self, span: Span) -> None:
        """Save a single span to storage."""
        async with self._lock:
            await asyncio.to_thread(self._save_span_sync, span)

    def _save_span_sync(self, span: Span) -> None:
        """Synchronous implementation of save_span."""
        conn = self._get_connection()

        # Serialize complex fields
        attributes_json = self._encoder.encode(span.attributes).decode("utf-8")
        events_json = self._encoder.encode(span.events).decode("utf-8")
        resource_attrs_json = self._encoder.encode(span.resource_attributes).decode(
            "utf-8"
        )

        status_code = span.status.status_code if span.status else None
        status_desc = span.status.description if span.status else None

        # Insert or update span
        conn.execute(
            """
            INSERT OR REPLACE INTO spans (
                span_id, trace_id, parent_span_id, name, kind,
                start_time, end_time, duration_ms, attributes, events,
                status_code, status_description, resource_attributes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                span.span_id,
                span.trace_id,
                span.parent_span_id,
                span.name,
                span.kind,
                span.start_time,
                span.end_time,
                span.duration_ms,
                attributes_json,
                events_json,
                status_code,
                status_desc,
                resource_attrs_json,
            ),
        )

        # Update or create trace record
        self._update_trace_record(conn, span.trace_id)
        conn.commit()

    def _update_trace_record(self, conn: sqlite3.Connection, trace_id: str) -> None:
        """Update trace aggregated data."""
        # Get all spans for this trace
        rows = conn.execute(
            """
            SELECT
                MIN(start_time) as min_start,
                MAX(end_time) as max_end,
                COUNT(*) as span_count,
                SUM(CASE WHEN status_code = 'ERROR' THEN 1 ELSE 0 END) as error_count
            FROM spans
            WHERE trace_id = ?
        """,
            (trace_id,),
        ).fetchone()

        if not rows or rows["span_count"] == 0:
            return

        min_start = rows["min_start"]
        max_end = rows["max_end"]
        span_count = rows["span_count"]
        error_count = rows["error_count"]
        duration_ms = (max_end - min_start) / 1_000_000

        # Get root span info
        root_span = conn.execute(
            """
            SELECT span_id, attributes, resource_attributes
            FROM spans
            WHERE trace_id = ? AND parent_span_id IS NULL
            LIMIT 1
        """,
            (trace_id,),
        ).fetchone()

        root_span_id = None
        service_name = None
        workflow_name = None

        if root_span:
            root_span_id = root_span["span_id"]
            attrs = json.loads(root_span["attributes"])
            resource_attrs = json.loads(root_span["resource_attributes"])

            workflow_name = attrs.get("msgflux.workflow.name")
            service_name = resource_attrs.get("service.name")

        # Insert or update trace
        conn.execute(
            """
            INSERT OR REPLACE INTO traces (
                trace_id, start_time, end_time, duration_ms,
                root_span_id, service_name, workflow_name,
                span_count, error_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                trace_id,
                min_start,
                max_end,
                duration_ms,
                root_span_id,
                service_name,
                workflow_name,
                span_count,
                error_count,
            ),
        )

    async def save_spans(self, spans: List[Span]) -> None:
        """Save multiple spans to storage."""
        async with self._lock:
            await asyncio.to_thread(self._save_spans_sync, spans)

    def _save_spans_sync(self, spans: List[Span]) -> None:
        """Synchronous implementation of save_spans."""
        conn = self._get_connection()
        for span in spans:
            self._save_span_sync(span)

    async def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a complete trace by its ID."""
        async with self._lock:
            return await asyncio.to_thread(self._get_trace_sync, trace_id)

    def _get_trace_sync(self, trace_id: str) -> Optional[Trace]:
        """Synchronous implementation of get_trace."""
        conn = self._get_connection()

        # Get trace metadata
        trace_row = conn.execute(
            "SELECT * FROM traces WHERE trace_id = ?", (trace_id,)
        ).fetchone()

        if not trace_row:
            return None

        # Get all spans
        span_rows = conn.execute(
            "SELECT * FROM spans WHERE trace_id = ? ORDER BY start_time",
            (trace_id,),
        ).fetchall()

        spans = []
        for row in span_rows:
            status = None
            if row["status_code"]:
                status = SpanStatus(
                    status_code=row["status_code"],
                    description=row["status_description"],
                )

            events = self._decoder.decode(row["events"].encode("utf-8"))
            events_list = [SpanEvent(**e) for e in events]

            span = Span(
                span_id=row["span_id"],
                trace_id=row["trace_id"],
                parent_span_id=row["parent_span_id"],
                name=row["name"],
                kind=row["kind"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                attributes=self._decoder.decode(row["attributes"].encode("utf-8")),
                events=events_list,
                status=status,
                resource_attributes=self._decoder.decode(
                    row["resource_attributes"].encode("utf-8")
                ),
            )
            spans.append(span)

        metadata = {}
        if trace_row["metadata"]:
            metadata = json.loads(trace_row["metadata"])

        return Trace(
            trace_id=trace_id,
            spans=spans,
            start_time=trace_row["start_time"],
            end_time=trace_row["end_time"],
            root_span_id=trace_row["root_span_id"],
            service_name=trace_row["service_name"],
            workflow_name=trace_row["workflow_name"],
            metadata=metadata,
        )

    async def list_traces(self, params: TraceQueryParams) -> List[TraceSummary]:
        """List traces matching the query parameters."""
        async with self._lock:
            return await asyncio.to_thread(self._list_traces_sync, params)

    def _list_traces_sync(self, params: TraceQueryParams) -> List[TraceSummary]:
        """Synchronous implementation of list_traces."""
        conn = self._get_connection()

        # Build query
        query = "SELECT * FROM traces WHERE 1=1"
        query_params = []

        if params.service_name:
            query += " AND service_name = ?"
            query_params.append(params.service_name)

        if params.workflow_name:
            query += " AND workflow_name = ?"
            query_params.append(params.workflow_name)

        if params.min_duration_ms:
            query += " AND duration_ms >= ?"
            query_params.append(params.min_duration_ms)

        if params.max_duration_ms:
            query += " AND duration_ms <= ?"
            query_params.append(params.max_duration_ms)

        if params.has_errors is not None:
            if params.has_errors:
                query += " AND error_count > 0"
            else:
                query += " AND error_count = 0"

        if params.start_time:
            query += " AND start_time >= ?"
            query_params.append(int(params.start_time.timestamp() * 1_000_000_000))

        if params.end_time:
            query += " AND end_time <= ?"
            query_params.append(int(params.end_time.timestamp() * 1_000_000_000))

        query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        query_params.extend([params.limit, params.offset])

        rows = conn.execute(query, query_params).fetchall()

        summaries = []
        for row in rows:
            # Get root span name
            root_span_name = None
            if row["root_span_id"]:
                root_span_row = conn.execute(
                    "SELECT name FROM spans WHERE span_id = ?", (row["root_span_id"],)
                ).fetchone()
                if root_span_row:
                    root_span_name = root_span_row["name"]

            summaries.append(
                TraceSummary(
                    trace_id=row["trace_id"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    duration_ms=row["duration_ms"],
                    span_count=row["span_count"],
                    error_count=row["error_count"],
                    service_name=row["service_name"],
                    workflow_name=row["workflow_name"],
                    root_span_name=root_span_name,
                )
            )

        return summaries

    async def get_span(self, span_id: str) -> Optional[Span]:
        """Get a single span by its ID."""
        async with self._lock:
            return await asyncio.to_thread(self._get_span_sync, span_id)

    def _get_span_sync(self, span_id: str) -> Optional[Span]:
        """Synchronous implementation of get_span."""
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM spans WHERE span_id = ?", (span_id,)).fetchone()

        if not row:
            return None

        status = None
        if row["status_code"]:
            status = SpanStatus(
                status_code=row["status_code"],
                description=row["status_description"],
            )

        events = self._decoder.decode(row["events"].encode("utf-8"))
        events_list = [SpanEvent(**e) for e in events]

        return Span(
            span_id=row["span_id"],
            trace_id=row["trace_id"],
            parent_span_id=row["parent_span_id"],
            name=row["name"],
            kind=row["kind"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            attributes=self._decoder.decode(row["attributes"].encode("utf-8")),
            events=events_list,
            status=status,
            resource_attributes=self._decoder.decode(
                row["resource_attributes"].encode("utf-8")
            ),
        )

    async def delete_trace(self, trace_id: str) -> bool:
        """Delete a trace and all its spans."""
        async with self._lock:
            return await asyncio.to_thread(self._delete_trace_sync, trace_id)

    def _delete_trace_sync(self, trace_id: str) -> bool:
        """Synchronous implementation of delete_trace."""
        conn = self._get_connection()
        cursor = conn.execute("DELETE FROM traces WHERE trace_id = ?", (trace_id,))
        conn.commit()
        return cursor.rowcount > 0

    async def count_traces(self, params: TraceQueryParams) -> int:
        """Count traces matching the query parameters."""
        async with self._lock:
            return await asyncio.to_thread(self._count_traces_sync, params)

    def _count_traces_sync(self, params: TraceQueryParams) -> int:
        """Synchronous implementation of count_traces."""
        conn = self._get_connection()

        # Build query (similar to list_traces)
        query = "SELECT COUNT(*) as count FROM traces WHERE 1=1"
        query_params = []

        if params.service_name:
            query += " AND service_name = ?"
            query_params.append(params.service_name)

        if params.workflow_name:
            query += " AND workflow_name = ?"
            query_params.append(params.workflow_name)

        if params.min_duration_ms:
            query += " AND duration_ms >= ?"
            query_params.append(params.min_duration_ms)

        if params.max_duration_ms:
            query += " AND duration_ms <= ?"
            query_params.append(params.max_duration_ms)

        if params.has_errors is not None:
            if params.has_errors:
                query += " AND error_count > 0"
            else:
                query += " AND error_count = 0"

        if params.start_time:
            query += " AND start_time >= ?"
            query_params.append(int(params.start_time.timestamp() * 1_000_000_000))

        if params.end_time:
            query += " AND end_time <= ?"
            query_params.append(int(params.end_time.timestamp() * 1_000_000_000))

        row = conn.execute(query, query_params).fetchone()
        return row["count"] if row else 0

    async def close(self) -> None:
        """Close the storage connection."""
        async with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
