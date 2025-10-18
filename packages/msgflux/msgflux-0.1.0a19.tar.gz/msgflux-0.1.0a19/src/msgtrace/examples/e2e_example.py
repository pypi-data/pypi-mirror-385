#!/usr/bin/env python3
"""
Complete end-to-end example of msgtrace with msgflux.

This example demonstrates:
1. Starting the msgtrace server
2. Running msgflux workflows with tracing
3. Querying and analyzing the captured traces
4. Viewing traces in the web UI
"""

import asyncio
import time
from pathlib import Path

from msgtrace.integration import quick_start

# Check if msgflux is available
try:
    from msgflux.message import Message
    from msgflux.nn import Predictor, Agent, Tool
    from msgflux import set_envs
except ImportError:
    print("❌ msgflux is not installed.")
    print("Install it with: pip install msgflux")
    exit(1)


# Define example tools for the agent
@Tool
def get_current_time() -> str:
    """Get the current time.

    Returns:
        Current time as a string
    """
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@Tool
def calculate(expression: str) -> float:
    """Calculate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result of the calculation
    """
    try:
        # Safe evaluation (use a proper math parser in production)
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        return f"Error: {e}"


@Tool
def generate_report(data: dict) -> str:
    """Generate a simple report from data.

    Args:
        data: Dictionary with report data

    Returns:
        Formatted report string
    """
    report = "=== Report ===\n"
    for key, value in data.items():
        report += f"{key}: {value}\n"
    return report


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


async def main():
    """Run the complete end-to-end example."""
    print_section("msgtrace - Complete End-to-End Example")

    # Step 1: Start msgtrace server
    print("📡 Step 1: Starting msgtrace server...")
    observer = quick_start(
        port=4321,
        enable_state_dict=True,
        enable_platform=True,
    )
    print("✅ Server started at http://localhost:4321")
    print("📊 Web UI: http://localhost:4321")
    print("📖 API Docs: http://localhost:4321/docs")

    time.sleep(2)  # Give server time to start

    # Step 2: Run a simple workflow
    print_section("Step 2: Running Simple Predictor Workflow")

    predictor = Predictor(
        name="sentiment_classifier",
        task_template="Classify the sentiment of this text: '{text}'",
        generation_schema={
            "sentiment": str,  # positive, negative, neutral
            "confidence": float,
            "reasoning": str,
        },
    )

    test_messages = [
        "This product is absolutely amazing! I love it!",
        "Terrible experience, very disappointed.",
        "It's okay, nothing special.",
    ]

    print("Running predictions with sentiment classifier...")
    for i, text in enumerate(test_messages, 1):
        print(f"\n[{i}/{len(test_messages)}] Processing: {text[:50]}...")
        message = Message(inputs={"text": text})

        try:
            result = predictor(message)
            output = result.get("outputs")
            print(f"   Sentiment: {output.get('sentiment')}")
            print(f"   Confidence: {output.get('confidence'):.0%}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Step 3: Run an agent workflow
    print_section("Step 3: Running Agent Workflow")

    agent = Agent(
        name="multi_tool_agent",
        tools=[get_current_time, calculate, generate_report],
        system_prompt="You are a helpful assistant. Use the available tools to complete tasks.",
    )

    agent_tasks = [
        "What is the current time?",
        "Calculate 15 * 24 + 100",
        "Generate a report with name='Test' and status='Complete'",
    ]

    print("Running agent tasks...")
    for i, task in enumerate(agent_tasks, 1):
        print(f"\n[{i}/{len(agent_tasks)}] Task: {task}")
        message = Message(inputs={"task": task})

        try:
            result = agent(message)
            response = result.get("outputs.response")
            print(f"   Response: {response[:100]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Step 4: Query traces via API
    print_section("Step 4: Querying Traces via API")

    from msgtrace.backend.storage import SQLiteTraceStorage
    from msgtrace.core.models import TraceQueryParams

    storage = SQLiteTraceStorage("msgtrace.db")

    # Get all traces
    print("📊 Fetching all traces...")
    all_traces = await storage.list_traces(TraceQueryParams(limit=100))
    print(f"   Total traces: {len(all_traces)}")

    if all_traces:
        print("\n📋 Recent Traces:")
        for trace in all_traces[:5]:
            status = "❌" if trace.error_count > 0 else "✅"
            print(f"   {status} {trace.workflow_name or 'Unknown'}")
            print(f"      Duration: {trace.duration_ms:.2f}ms")
            print(f"      Spans: {trace.span_count} | Errors: {trace.error_count}")
            print(f"      ID: {trace.trace_id[:32]}...")

        # Get detailed trace
        print("\n🔍 Detailed View of First Trace:")
        first_trace = await storage.get_trace(all_traces[0].trace_id)
        print(f"   Trace ID: {first_trace.trace_id}")
        print(f"   Workflow: {first_trace.workflow_name}")
        print(f"   Duration: {first_trace.duration_ms:.2f}ms")
        print(f"   Total Spans: {len(first_trace.spans)}")

        # Build span tree
        tree = first_trace.build_span_tree()

        def print_tree(node, depth=0):
            """Recursively print span tree."""
            span = node["span"]
            indent = "  " * depth
            status = "❌" if span.status and span.status.status_code == "ERROR" else "✅"
            duration_ms = (span.end_time - span.start_time) / 1_000_000
            print(f"{indent}{status} {span.name} ({duration_ms:.2f}ms)")
            for child in node.get("children", []):
                print_tree(child, depth + 1)

        if tree:
            print("\n   Span Tree:")
            print_tree(tree, 2)

        # Show token and cost information
        print("\n💰 Token & Cost Analysis:")
        total_tokens = 0
        total_cost = 0.0

        for span in first_trace.spans:
            tokens = span.attributes.get("llm.usage.total_tokens")
            cost = span.attributes.get("llm.cost.total")
            model = span.attributes.get("llm.model")

            if tokens or cost or model:
                print(f"\n   Span: {span.name}")
                if model:
                    print(f"      Model: {model}")
                if tokens:
                    print(f"      Tokens: {tokens:,}")
                    total_tokens += tokens
                if cost:
                    print(f"      Cost: ${cost:.6f}")
                    total_cost += cost

        if total_tokens > 0:
            print(f"\n   📊 Total Tokens: {total_tokens:,}")
        if total_cost > 0:
            print(f"   💵 Total Cost: ${total_cost:.6f}")

    await storage.close()

    # Step 5: Show how to access the web UI
    print_section("Step 5: Explore in Web UI")
    print("🌐 Open your browser and visit:")
    print("   • Dashboard: http://localhost:4321/dashboard")
    print("   • Trace List: http://localhost:4321/traces")
    print("   • API Docs: http://localhost:4321/docs")
    print("\n📊 Features to explore:")
    print("   ✓ Timeline visualization")
    print("   ✓ Span tree (hierarchical view)")
    print("   ✓ Token usage and costs")
    print("   ✓ Error highlighting")
    print("   ✓ Search and filtering")
    print("   ✓ Detailed span information")

    # Step 6: Keep server running
    print_section("Step 6: Server Running")
    print("The msgtrace server is now running and capturing traces.")
    print("\n💡 Tips:")
    print("   • Run your msgflux workflows and traces will appear automatically")
    print("   • Refresh the web UI to see new traces")
    print("   • Use filters to find specific traces")
    print("   • Click on any trace to see detailed analysis")
    print("\nPress Ctrl+C to stop the server...")

    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        observer.stop()
        print("✅ Server stopped. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
