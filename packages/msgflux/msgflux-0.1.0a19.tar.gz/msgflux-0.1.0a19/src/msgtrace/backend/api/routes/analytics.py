"""
Analytics REST API endpoints for advanced metrics
"""

from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional
import statistics

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_trace_storage():
    """Get trace storage instance - will be injected by app"""
    return None


@router.get("/latency-percentiles")
async def get_latency_percentiles(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    workflow_name: Optional[str] = Query(None, description="Filter by workflow"),
    service_name: Optional[str] = Query(None, description="Filter by service"),
):
    """
    Get latency percentiles (P50, P95, P99) for traces.

    Args:
        hours: Time window in hours (default 24)
        workflow_name: Optional workflow filter
        service_name: Optional service filter

    Returns:
        Percentile metrics
    """
    storage = get_trace_storage()

    # Calculate time range
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)

    # Get traces
    from msgtrace.core.models import TraceQueryParams
    traces = await storage.list_traces(
        TraceQueryParams(
            limit=10000,  # Get enough for statistics
            workflow_name=workflow_name,
            service_name=service_name,
        )
    )

    # Filter by time range
    traces = [t for t in traces if start_time <= t.start_time <= end_time]

    if not traces:
        return {
            "p50": 0,
            "p95": 0,
            "p99": 0,
            "count": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
        }

    # Extract durations
    durations = [t.duration_ms for t in traces]
    durations.sort()

    # Calculate percentiles
    p50 = statistics.median(durations)
    p95 = durations[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
    p99 = durations[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0]

    return {
        "p50": round(p50, 2),
        "p95": round(p95, 2),
        "p99": round(p99, 2),
        "count": len(durations),
        "mean": round(statistics.mean(durations), 2),
        "min": round(min(durations), 2),
        "max": round(max(durations), 2),
        "time_window_hours": hours,
        "workflow_name": workflow_name,
        "service_name": service_name,
    }


@router.get("/timeseries/latency")
async def get_latency_timeseries(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    bucket_minutes: int = Query(60, ge=5, le=1440, description="Bucket size in minutes"),
    workflow_name: Optional[str] = Query(None, description="Filter by workflow"),
):
    """
    Get latency metrics over time in buckets.

    Returns time series data for charting.
    """
    storage = get_trace_storage()

    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    bucket_size = timedelta(minutes=bucket_minutes)

    # Get traces
    from msgtrace.core.models import TraceQueryParams
    traces = await storage.list_traces(
        TraceQueryParams(
            limit=10000,
            workflow_name=workflow_name,
        )
    )

    # Filter by time range
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)
    traces = [t for t in traces if start_time_ms <= t.start_time <= end_time_ms]

    # Create buckets
    buckets = []
    current = start_time
    while current < end_time:
        bucket_start = int(current.timestamp() * 1000)
        bucket_end = int((current + bucket_size).timestamp() * 1000)

        # Get traces in this bucket
        bucket_traces = [
            t for t in traces
            if bucket_start <= t.start_time < bucket_end
        ]

        if bucket_traces:
            durations = [t.duration_ms for t in bucket_traces]
            durations.sort()

            buckets.append({
                "timestamp": int(current.timestamp() * 1000),
                "time": current.isoformat(),
                "count": len(bucket_traces),
                "p50": round(statistics.median(durations), 2),
                "p95": round(durations[int(len(durations) * 0.95)], 2) if len(durations) > 1 else durations[0],
                "mean": round(statistics.mean(durations), 2),
                "min": round(min(durations), 2),
                "max": round(max(durations), 2),
            })
        else:
            buckets.append({
                "timestamp": int(current.timestamp() * 1000),
                "time": current.isoformat(),
                "count": 0,
                "p50": 0,
                "p95": 0,
                "mean": 0,
                "min": 0,
                "max": 0,
            })

        current += bucket_size

    return {
        "buckets": buckets,
        "total_traces": len(traces),
        "time_window_hours": hours,
        "bucket_minutes": bucket_minutes,
    }


@router.get("/timeseries/errors")
async def get_error_timeseries(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    bucket_minutes: int = Query(60, ge=5, le=1440, description="Bucket size in minutes"),
    workflow_name: Optional[str] = Query(None, description="Filter by workflow"),
):
    """
    Get error rate metrics over time.
    """
    storage = get_trace_storage()

    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    bucket_size = timedelta(minutes=bucket_minutes)

    # Get traces
    from msgtrace.core.models import TraceQueryParams
    traces = await storage.list_traces(
        TraceQueryParams(
            limit=10000,
            workflow_name=workflow_name,
        )
    )

    # Filter by time range
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)
    traces = [t for t in traces if start_time_ms <= t.start_time <= end_time_ms]

    # Create buckets
    buckets = []
    current = start_time
    while current < end_time:
        bucket_start = int(current.timestamp() * 1000)
        bucket_end = int((current + bucket_size).timestamp() * 1000)

        # Get traces in this bucket
        bucket_traces = [
            t for t in traces
            if bucket_start <= t.start_time < bucket_end
        ]

        if bucket_traces:
            total = len(bucket_traces)
            errors = sum(1 for t in bucket_traces if t.error_count > 0)
            error_rate = (errors / total) * 100 if total > 0 else 0

            buckets.append({
                "timestamp": int(current.timestamp() * 1000),
                "time": current.isoformat(),
                "total_traces": total,
                "error_traces": errors,
                "error_rate": round(error_rate, 2),
                "success_rate": round(100 - error_rate, 2),
            })
        else:
            buckets.append({
                "timestamp": int(current.timestamp() * 1000),
                "time": current.isoformat(),
                "total_traces": 0,
                "error_traces": 0,
                "error_rate": 0,
                "success_rate": 100,
            })

        current += bucket_size

    return {
        "buckets": buckets,
        "total_traces": len(traces),
        "time_window_hours": hours,
        "bucket_minutes": bucket_minutes,
    }


@router.get("/timeseries/throughput")
async def get_throughput_timeseries(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    bucket_minutes: int = Query(60, ge=5, le=1440, description="Bucket size in minutes"),
    workflow_name: Optional[str] = Query(None, description="Filter by workflow"),
):
    """
    Get trace throughput over time (traces per time unit).
    """
    storage = get_trace_storage()

    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    bucket_size = timedelta(minutes=bucket_minutes)

    # Get traces
    from msgtrace.core.models import TraceQueryParams
    traces = await storage.list_traces(
        TraceQueryParams(
            limit=10000,
            workflow_name=workflow_name,
        )
    )

    # Filter by time range
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)
    traces = [t for t in traces if start_time_ms <= t.start_time <= end_time_ms]

    # Create buckets
    buckets = []
    current = start_time
    while current < end_time:
        bucket_start = int(current.timestamp() * 1000)
        bucket_end = int((current + bucket_size).timestamp() * 1000)

        # Count traces in this bucket
        count = sum(
            1 for t in traces
            if bucket_start <= t.start_time < bucket_end
        )

        buckets.append({
            "timestamp": int(current.timestamp() * 1000),
            "time": current.isoformat(),
            "count": count,
            "rate_per_minute": round(count / bucket_minutes, 2),
        })

        current += bucket_size

    return {
        "buckets": buckets,
        "total_traces": len(traces),
        "time_window_hours": hours,
        "bucket_minutes": bucket_minutes,
    }


@router.get("/workflow-comparison")
async def get_workflow_comparison(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
):
    """
    Compare performance metrics across different workflows.
    """
    storage = get_trace_storage()

    # Calculate time range
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)

    # Get all traces
    from msgtrace.core.models import TraceQueryParams
    traces = await storage.list_traces(TraceQueryParams(limit=10000))

    # Filter by time range
    traces = [t for t in traces if start_time <= t.start_time <= end_time]

    # Group by workflow
    workflows = {}
    for trace in traces:
        workflow = trace.workflow_name or "unknown"
        if workflow not in workflows:
            workflows[workflow] = []
        workflows[workflow].append(trace)

    # Calculate metrics for each workflow
    comparison = []
    for workflow, workflow_traces in workflows.items():
        if not workflow_traces:
            continue

        durations = sorted([t.duration_ms for t in workflow_traces])
        errors = sum(1 for t in workflow_traces if t.error_count > 0)
        total = len(workflow_traces)

        comparison.append({
            "workflow_name": workflow,
            "count": total,
            "p50": round(statistics.median(durations), 2),
            "p95": round(durations[int(len(durations) * 0.95)], 2) if len(durations) > 1 else durations[0],
            "mean": round(statistics.mean(durations), 2),
            "error_count": errors,
            "error_rate": round((errors / total) * 100, 2) if total > 0 else 0,
        })

    # Sort by count descending
    comparison.sort(key=lambda x: x["count"], reverse=True)

    return {
        "workflows": comparison,
        "total_workflows": len(comparison),
        "time_window_hours": hours,
    }
