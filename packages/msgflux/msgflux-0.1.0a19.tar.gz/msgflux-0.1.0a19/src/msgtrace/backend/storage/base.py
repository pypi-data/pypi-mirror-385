"""Base interface for trace storage."""

from abc import ABC, abstractmethod
from typing import List, Optional

from msgtrace.core.models import Span, Trace, TraceQueryParams, TraceSummary


class TraceStorage(ABC):
    """Abstract base class for trace storage backends."""

    @abstractmethod
    async def save_span(self, span: Span) -> None:
        """Save a single span to storage.

        Args:
            span: Span to save
        """
        pass

    @abstractmethod
    async def save_spans(self, spans: List[Span]) -> None:
        """Save multiple spans to storage (batch operation).

        Args:
            spans: List of spans to save
        """
        pass

    @abstractmethod
    async def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a complete trace by its ID.

        Args:
            trace_id: ID of the trace to retrieve

        Returns:
            Trace object with all spans, or None if not found
        """
        pass

    @abstractmethod
    async def list_traces(self, params: TraceQueryParams) -> List[TraceSummary]:
        """List traces matching the query parameters.

        Args:
            params: Query parameters for filtering traces

        Returns:
            List of trace summaries
        """
        pass

    @abstractmethod
    async def get_span(self, span_id: str) -> Optional[Span]:
        """Get a single span by its ID.

        Args:
            span_id: ID of the span to retrieve

        Returns:
            Span object or None if not found
        """
        pass

    @abstractmethod
    async def delete_trace(self, trace_id: str) -> bool:
        """Delete a trace and all its spans.

        Args:
            trace_id: ID of the trace to delete

        Returns:
            True if trace was deleted, False if not found
        """
        pass

    @abstractmethod
    async def count_traces(self, params: TraceQueryParams) -> int:
        """Count traces matching the query parameters.

        Args:
            params: Query parameters for filtering traces

        Returns:
            Number of matching traces
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the storage connection and cleanup resources."""
        pass
