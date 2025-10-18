# msgtrace Examples

This directory contains example scripts demonstrating how to use msgtrace.

## Examples

### 1. `basic_tracing.py`
Basic example showing how to trace simple Predictor workflows.

```bash
python -m msgtrace.examples.basic_tracing
```

**What it demonstrates:**
- Starting msgtrace server with `quick_start()`
- Running Predictor with automatic tracing
- Viewing traces in the web UI

---

### 2. `agent_tracing.py`
Example showing how to trace Agent workflows with multiple tools.

```bash
python -m msgtrace.examples.agent_tracing
```

**What it demonstrates:**
- Tracing Agent workflows
- Capturing tool executions
- Extended telemetry (state_dict, platform info)
- Multi-step agent reasoning traces

---

### 3. `query_traces.py`
Example showing how to query and analyze traces programmatically.

```bash
python -m msgtrace.examples.query_traces
```

**What it demonstrates:**
- Querying traces from storage
- Filtering traces by criteria
- Analyzing performance metrics
- Building span trees
- Calculating aggregates (avg duration, error rates, etc.)

---

### 4. `e2e_example.py` ⭐ (Recommended Starting Point)
Complete end-to-end example demonstrating the full workflow.

```bash
python -m msgtrace.examples.e2e_example
```

**What it demonstrates:**
- Starting the msgtrace server
- Running multiple workflow types (Predictor + Agent)
- Querying traces via API
- Analyzing token usage and costs
- Accessing the web UI
- Complete workflow from start to finish

**Output includes:**
- ✅ Server startup confirmation
- 📊 Workflow execution results
- 🔍 Trace query examples
- 💰 Token and cost analysis
- 🌐 Links to web UI

---

## Quick Start

### 1. Run the Complete Example

```bash
# This is the best place to start!
python -m msgtrace.examples.e2e_example
```

Then open http://localhost:4321 in your browser to explore the web UI.

### 2. Run Individual Examples

```bash
# Basic tracing
python -m msgtrace.examples.basic_tracing

# Agent tracing
python -m msgtrace.examples.agent_tracing

# Query traces
python -m msgtrace.examples.query_traces
```

---

## Prerequisites

All examples require msgflux to be installed:

```bash
pip install msgflux
```

Some examples also need OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

---

## What Gets Traced?

msgtrace automatically captures:

### Module Execution
- Module name and type
- Start/End timestamps
- Duration
- Input/Output data (optional)
- State changes (optional)

### Tool Calls
- Tool name and parameters
- Execution time
- Return values
- Errors and exceptions

### LLM Requests
- Model name
- Token usage (input/output/total)
- Costs (input/output/total)
- Latency
- Request/Response (optional)

### Errors
- Exception type and message
- Stack traces
- Failed span identification

---

## Customizing Telemetry

### Basic Configuration

```python
from msgtrace.integration import quick_start

observer = quick_start(
    port=4321,
    enable_state_dict=True,        # Capture module states
    enable_platform=True,           # Capture platform info
    enable_tool_responses=True,     # Capture tool outputs
)
```

### Advanced Configuration

```python
from msgtrace.core.config import MsgTraceConfig
from msgtrace.core.client import start_observer

config = MsgTraceConfig(
    host="0.0.0.0",
    port=4321,
    db_path="./traces/msgtrace.db",
    cors_origins=["http://localhost:3000"],
    queue_size=1000,
)

observer = start_observer(config=config)
```

### msgflux Configuration

```python
from msgflux import set_envs

set_envs(
    telemetry_requires_trace=True,
    telemetry_span_exporter_type="otlp",
    telemetry_otlp_endpoint="http://localhost:4321/api/v1/traces/export",

    # Extended telemetry
    telemetry_capture_state_dict=True,
    telemetry_capture_platform=True,
    telemetry_capture_tool_call_responses=True,
)
```

---

## Analyzing Traces

### Via Web UI (Easiest)

1. Start server: `msgtrace start`
2. Run workflows
3. Open http://localhost:4321
4. Explore traces in the dashboard

### Via Python API

```python
import asyncio
from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams

async def analyze():
    storage = SQLiteTraceStorage("msgtrace.db")

    # List all traces
    traces = await storage.list_traces(TraceQueryParams(limit=10))

    # Get detailed trace
    trace = await storage.get_trace(traces[0].trace_id)

    # Build span tree
    tree = trace.build_span_tree()

    await storage.close()

asyncio.run(analyze())
```

### Via CLI

```bash
# Show statistics
msgtrace stats

# List recent traces
msgtrace list --limit 10

# Show specific trace
msgtrace show <trace-id>
```

### Via API

```bash
# List traces
curl http://localhost:4321/api/v1/traces

# Get specific trace
curl http://localhost:4321/api/v1/traces/<trace-id>

# Get span tree
curl http://localhost:4321/api/v1/traces/<trace-id>/tree

# Get statistics
curl http://localhost:4321/api/v1/stats
```

---

## Common Use Cases

### Debug Slow Workflows

```python
# Find traces over 1 second
params = TraceQueryParams(min_duration_ms=1000)
slow_traces = await storage.list_traces(params)

# Analyze bottlenecks
for trace in slow_traces:
    full_trace = await storage.get_trace(trace.trace_id)
    for span in full_trace.spans:
        if span.duration_ms > 500:
            print(f"Slow span: {span.name} - {span.duration_ms}ms")
```

### Monitor Errors

```python
# Find error traces
params = TraceQueryParams(has_errors=True)
error_traces = await storage.list_traces(params)

# Analyze error patterns
for trace in error_traces:
    full_trace = await storage.get_trace(trace.trace_id)
    for span in full_trace.spans:
        if span.is_error():
            print(f"Error in {span.name}: {span.status.description}")
```

### Track Costs

```python
# Calculate total costs
total_cost = 0.0
for span in trace.spans:
    cost = span.attributes.get("llm.cost.total", 0)
    total_cost += cost

print(f"Total cost: ${total_cost:.6f}")
```

### Compare Executions

```python
trace1 = await storage.get_trace(id1)
trace2 = await storage.get_trace(id2)

print(f"Trace 1: {trace1.duration_ms:.2f}ms")
print(f"Trace 2: {trace2.duration_ms:.2f}ms")
print(f"Difference: {abs(trace1.duration_ms - trace2.duration_ms):.2f}ms")
```

---

## Tips

1. **Start with e2e_example.py** - It shows the complete workflow
2. **Keep the server running** - Traces are captured automatically
3. **Use the web UI** - It's the easiest way to explore traces
4. **Filter traces** - Use the search and filter features
5. **Analyze patterns** - Look for common bottlenecks and errors
6. **Export data** - Use the API to export traces for further analysis

---

## Troubleshooting

### "No traces found"

- Make sure msgtrace server is running
- Verify msgflux telemetry is enabled
- Check OTLP endpoint configuration
- Run an example workflow to generate traces

### "Connection refused"

- Ensure msgtrace is running on the correct port
- Check firewall settings
- Verify the endpoint URL

### "Import errors"

- Install msgflux: `pip install msgflux`
- Install msgtrace: `pip install -e .`
- Check Python version (3.11+ recommended)

---

## Next Steps

- Explore the web UI at http://localhost:4321
- Read the full documentation in README.md
- Check deployment options in DEPLOYMENT.md
- Customize telemetry for your use case
- Integrate with your CI/CD pipeline

Happy tracing! 🎉
