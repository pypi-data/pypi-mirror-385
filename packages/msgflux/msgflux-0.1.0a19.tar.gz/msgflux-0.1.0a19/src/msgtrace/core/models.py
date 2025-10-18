"""Data models for traces and spans."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import msgspec


class SpanStatus(msgspec.Struct):
    """Status of a span execution."""

    status_code: str  # OK, ERROR, UNSET
    description: Optional[str] = None


class SpanEvent(msgspec.Struct):
    """Event that occurred during span execution."""

    name: str
    timestamp: int  # Unix timestamp in nanoseconds
    attributes: Dict[str, Any] = msgspec.field(default_factory=dict)


class Span(msgspec.Struct):
    """Represents a single span in a trace.

    A span represents a unit of work or operation in the system,
    such as a module execution, tool call, or API request.
    """

    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    name: str
    kind: str  # INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER
    start_time: int  # Unix timestamp in nanoseconds
    end_time: int  # Unix timestamp in nanoseconds
    attributes: Dict[str, Any] = msgspec.field(default_factory=dict)
    events: List[SpanEvent] = msgspec.field(default_factory=list)
    status: Optional[SpanStatus] = None
    resource_attributes: Dict[str, Any] = msgspec.field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Duration of the span in milliseconds."""
        return (self.end_time - self.start_time) / 1_000_000

    @property
    def duration_ns(self) -> int:
        """Duration of the span in nanoseconds."""
        return self.end_time - self.start_time

    def is_root(self) -> bool:
        """Check if this is a root span (no parent)."""
        return self.parent_span_id is None

    def is_error(self) -> bool:
        """Check if the span ended with an error."""
        return self.status is not None and self.status.status_code == "ERROR"


class Trace(msgspec.Struct):
    """Represents a complete trace with all its spans.

    A trace represents a complete workflow execution,
    containing all spans from root to leaves.
    """

    trace_id: str
    spans: List[Span] = msgspec.field(default_factory=list)
    start_time: int  # Unix timestamp in nanoseconds
    end_time: int  # Unix timestamp in nanoseconds
    root_span_id: Optional[str] = None
    service_name: Optional[str] = None
    workflow_name: Optional[str] = None
    metadata: Dict[str, Any] = msgspec.field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Total duration of the trace in milliseconds."""
        return (self.end_time - self.start_time) / 1_000_000

    @property
    def span_count(self) -> int:
        """Number of spans in this trace."""
        return len(self.spans)

    @property
    def error_count(self) -> int:
        """Number of spans that ended with errors."""
        return sum(1 for span in self.spans if span.is_error())

    def get_root_span(self) -> Optional[Span]:
        """Get the root span of this trace."""
        if self.root_span_id:
            return next(
                (s for s in self.spans if s.span_id == self.root_span_id), None
            )
        return next((s for s in self.spans if s.is_root()), None)

    def get_span_by_id(self, span_id: str) -> Optional[Span]:
        """Get a span by its ID."""
        return next((s for s in self.spans if s.span_id == span_id), None)

    def get_children(self, span_id: str) -> List[Span]:
        """Get all direct children of a span."""
        return [s for s in self.spans if s.parent_span_id == span_id]

    def build_span_tree(self) -> Dict[str, Any]:
        """Build a tree structure of spans for visualization."""
        root = self.get_root_span()
        if not root:
            return {}

        def build_node(span: Span) -> Dict[str, Any]:
            children = self.get_children(span.span_id)
            return {
                "span": span,
                "children": [build_node(child) for child in children],
            }

        return build_node(root)


class TraceQueryParams(msgspec.Struct):
    """Parameters for querying traces."""

    service_name: Optional[str] = None
    workflow_name: Optional[str] = None
    min_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    has_errors: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class TraceSummary(msgspec.Struct):
    """Summary information about a trace for list views."""

    trace_id: str
    start_time: int
    end_time: int
    duration_ms: float
    span_count: int
    error_count: int
    service_name: Optional[str] = None
    workflow_name: Optional[str] = None
    root_span_name: Optional[str] = None
