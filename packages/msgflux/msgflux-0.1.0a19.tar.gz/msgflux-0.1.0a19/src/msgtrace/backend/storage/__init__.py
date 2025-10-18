"""Storage layer for msgtrace."""

from msgtrace.backend.storage.base import TraceStorage
from msgtrace.backend.storage.sqlite import SQLiteTraceStorage

__all__ = ["TraceStorage", "SQLiteTraceStorage"]
