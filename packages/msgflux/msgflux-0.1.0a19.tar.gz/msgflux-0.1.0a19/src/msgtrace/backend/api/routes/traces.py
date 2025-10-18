"""Trace-related API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from msgtrace.core.models import Trace, TraceQueryParams, TraceSummary

router = APIRouter(tags=["traces"])


# Pydantic models for request/response
class TraceQueryRequest(BaseModel):
    """Request model for trace queries."""

    service_name: Optional[str] = None
    workflow_name: Optional[str] = None
    min_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    has_errors: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TraceListResponse(BaseModel):
    """Response model for trace list."""

    traces: List[TraceSummary]
    total: int
    limit: int
    offset: int


class OTLPExportRequest(BaseModel):
    """Request model for OTLP trace export."""

    # This will accept the standard OTLP JSON format
    # The structure is flexible to handle any OTLP payload
    pass

    class Config:
        extra = "allow"


@router.post("/traces/export", status_code=202)
async def export_traces(request: Request, otlp_data: Dict[str, Any]):
    """Receive OTLP trace data for export.

    This endpoint receives trace data in OTLP format and queues it for processing.
    Compatible with OpenTelemetry exporters.

    Args:
        request: FastAPI request object
        otlp_data: OTLP formatted trace data

    Returns:
        Acceptance confirmation
    """
    collector = request.app.state.collector
    await collector.receive_traces(otlp_data)

    return {"status": "accepted", "message": "Trace data queued for processing"}


@router.get("/traces", response_model=TraceListResponse)
async def list_traces(
    request: Request,
    service_name: Optional[str] = None,
    workflow_name: Optional[str] = None,
    min_duration_ms: Optional[float] = None,
    max_duration_ms: Optional[float] = None,
    has_errors: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
):
    """List traces with optional filtering.

    Args:
        request: FastAPI request object
        service_name: Filter by service name
        workflow_name: Filter by workflow name
        min_duration_ms: Minimum duration in milliseconds
        max_duration_ms: Maximum duration in milliseconds
        has_errors: Filter by error presence
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of trace summaries with pagination info
    """
    storage = request.app.state.storage

    params = TraceQueryParams(
        service_name=service_name,
        workflow_name=workflow_name,
        min_duration_ms=min_duration_ms,
        max_duration_ms=max_duration_ms,
        has_errors=has_errors,
        limit=limit,
        offset=offset,
    )

    traces = await storage.list_traces(params)
    total = await storage.count_traces(params)

    return TraceListResponse(
        traces=traces,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/traces/{trace_id}", response_model=Trace)
async def get_trace(request: Request, trace_id: str):
    """Get detailed information about a specific trace.

    Args:
        request: FastAPI request object
        trace_id: ID of the trace to retrieve

    Returns:
        Complete trace with all spans

    Raises:
        HTTPException: If trace not found
    """
    storage = request.app.state.storage
    trace = await storage.get_trace(trace_id)

    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")

    return trace


@router.delete("/traces/{trace_id}", status_code=204)
async def delete_trace(request: Request, trace_id: str):
    """Delete a trace and all its spans.

    Args:
        request: FastAPI request object
        trace_id: ID of the trace to delete

    Returns:
        No content on success

    Raises:
        HTTPException: If trace not found
    """
    storage = request.app.state.storage
    deleted = await storage.delete_trace(trace_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Trace not found")

    return None


@router.get("/traces/{trace_id}/tree")
async def get_trace_tree(request: Request, trace_id: str):
    """Get trace span tree for visualization.

    Returns the trace spans organized in a tree structure,
    useful for hierarchical visualization.

    Args:
        request: FastAPI request object
        trace_id: ID of the trace

    Returns:
        Tree structure of spans

    Raises:
        HTTPException: If trace not found
    """
    storage = request.app.state.storage
    trace = await storage.get_trace(trace_id)

    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")

    tree = trace.build_span_tree()
    return tree


@router.get("/stats")
async def get_stats(request: Request):
    """Get overall statistics about traces.

    Returns:
        Statistics about stored traces
    """
    storage = request.app.state.storage

    # Get basic counts
    all_params = TraceQueryParams(limit=1)
    total_traces = await storage.count_traces(all_params)

    error_params = TraceQueryParams(has_errors=True, limit=1)
    error_traces = await storage.count_traces(error_params)

    return {
        "total_traces": total_traces,
        "traces_with_errors": error_traces,
        "error_rate": error_traces / total_traces if total_traces > 0 else 0,
    }
