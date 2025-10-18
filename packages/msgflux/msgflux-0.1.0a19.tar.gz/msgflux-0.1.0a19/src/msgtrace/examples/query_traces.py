"""Example of querying and analyzing traces."""

import asyncio

from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams


async def analyze_traces():
    """Analyze traces from the database."""
    storage = SQLiteTraceStorage("msgtrace.db")

    print("📊 Trace Analysis")
    print("=" * 70)

    # Get all traces
    all_params = TraceQueryParams(limit=1000)
    all_traces = await storage.list_traces(all_params)
    total_count = len(all_traces)

    print(f"\n📈 Summary:")
    print(f"  Total traces: {total_count}")

    if total_count == 0:
        print("\n⚠️  No traces found. Run a workflow with tracing enabled first.")
        await storage.close()
        return

    # Calculate statistics
    total_duration = sum(t.duration_ms for t in all_traces)
    avg_duration = total_duration / total_count if total_count > 0 else 0
    total_spans = sum(t.span_count for t in all_traces)
    total_errors = sum(t.error_count for t in all_traces)

    print(f"  Average duration: {avg_duration:.2f}ms")
    print(f"  Total spans: {total_spans}")
    print(f"  Total errors: {total_errors}")
    print(
        f"  Error rate: {(total_errors / total_spans * 100 if total_spans > 0 else 0):.2f}%"
    )

    # Find slowest traces
    print(f"\n🐌 Slowest Traces (Top 5):")
    slow_traces = sorted(all_traces, key=lambda t: t.duration_ms, reverse=True)[:5]
    for i, trace in enumerate(slow_traces, 1):
        print(
            f"  {i}. {trace.workflow_name or 'Unknown'}: {trace.duration_ms:.2f}ms ({trace.span_count} spans)"
        )

    # Find traces with errors
    error_params = TraceQueryParams(has_errors=True, limit=5)
    error_traces = await storage.list_traces(error_params)

    if error_traces:
        print(f"\n❌ Traces with Errors (Top 5):")
        for i, trace in enumerate(error_traces, 1):
            print(
                f"  {i}. {trace.workflow_name or 'Unknown'}: {trace.error_count} errors"
            )
    else:
        print(f"\n✅ No traces with errors!")

    # Analyze by workflow
    workflows = {}
    for trace in all_traces:
        name = trace.workflow_name or "Unknown"
        if name not in workflows:
            workflows[name] = {"count": 0, "total_duration": 0, "errors": 0}
        workflows[name]["count"] += 1
        workflows[name]["total_duration"] += trace.duration_ms
        workflows[name]["errors"] += trace.error_count

    print(f"\n📋 By Workflow:")
    for name, stats in workflows.items():
        avg = stats["total_duration"] / stats["count"]
        print(f"  {name}:")
        print(f"    Executions: {stats['count']}")
        print(f"    Avg duration: {avg:.2f}ms")
        print(f"    Errors: {stats['errors']}")

    # Get a detailed trace
    if all_traces:
        print(f"\n🔍 Detailed View (First Trace):")
        trace = await storage.get_trace(all_traces[0].trace_id)

        print(f"  Trace ID: {trace.trace_id}")
        print(f"  Workflow: {trace.workflow_name}")
        print(f"  Duration: {trace.duration_ms:.2f}ms")
        print(f"  Spans ({len(trace.spans)}):")

        # Build and display tree
        tree = trace.build_span_tree()

        def print_tree(node, depth=0):
            """Recursively print span tree."""
            span = node["span"]
            indent = "  " * depth
            status = "❌" if span.is_error() else "✅"
            print(
                f"{indent}{status} {span.name} ({span.duration_ms:.2f}ms)"
            )
            for child in node.get("children", []):
                print_tree(child, depth + 1)

        if tree:
            print_tree(tree)

    await storage.close()
    print("\n✅ Analysis complete!")


def main():
    """Entry point."""
    asyncio.run(analyze_traces())


if __name__ == "__main__":
    main()
