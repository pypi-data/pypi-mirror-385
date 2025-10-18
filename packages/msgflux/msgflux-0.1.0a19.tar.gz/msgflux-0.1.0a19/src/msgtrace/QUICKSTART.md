# msgtrace - Quick Start Guide

## 🚀 Get Started in 60 Seconds

### 1. Start the Server

**Option A: Python API (Recommended)**
```python
from msgtrace.integration import quick_start

# One line to rule them all!
observer = quick_start(port=4321)

# Your msgflux code here...
# Traces are automatically captured!

# Stop when done (or leave running)
# observer.stop()
```

**Option B: CLI**
```bash
msgtrace start --port 4321
```

### 2. Run Your msgflux Code

The telemetry is already configured! Just use msgflux normally:

```python
from msgflux.nn import Predictor
from msgflux.message import Message

predictor = Predictor(
    name="my_predictor",
    task_template="Analyze: {text}"
)

message = Message(inputs={"text": "Hello, world!"})
result = predictor(message)
```

### 3. View Your Traces

**API**
```bash
# List traces
curl http://localhost:4321/api/v1/traces

# Get specific trace
curl http://localhost:4321/api/v1/traces/{trace_id}

# View API docs
open http://localhost:4321/docs
```

**CLI**
```bash
# View statistics
msgtrace stats

# List recent traces
msgtrace list

# Show specific trace
msgtrace show {trace_id}
```

**Python**
```python
import asyncio
from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams

async def view_traces():
    storage = SQLiteTraceStorage("msgtrace.db")

    # List traces
    params = TraceQueryParams(limit=10)
    traces = await storage.list_traces(params)

    for trace in traces:
        print(f"{trace.workflow_name}: {trace.duration_ms:.2f}ms")

    await storage.close()

asyncio.run(view_traces())
```

## 🎯 Common Use Cases

### Use Case 1: Debug Slow Workflows

```python
# Find slow traces
from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams

async def find_slow():
    storage = SQLiteTraceStorage()

    # Traces over 1 second
    slow = await storage.list_traces(
        TraceQueryParams(min_duration_ms=1000)
    )

    for trace in slow:
        print(f"Slow: {trace.workflow_name} - {trace.duration_ms}ms")

        # Get details
        full_trace = await storage.get_trace(trace.trace_id)

        # Find bottleneck spans
        for span in full_trace.spans:
            if span.duration_ms > 500:
                print(f"  Bottleneck: {span.name} - {span.duration_ms}ms")
```

### Use Case 2: Monitor Errors

```bash
# Quick check
msgtrace stats

# List error traces
curl "http://localhost:4321/api/v1/traces?has_errors=true"
```

### Use Case 3: Analyze Agent Behavior

```python
from msgtrace.integration import quick_start

# Enable extended telemetry
observer = quick_start(
    enable_state_dict=True,    # Capture module states
    enable_platform=True,       # Capture platform info
)

# Your agent code...
# All tool calls and state transitions are captured!
```

### Use Case 4: Compare Executions

```python
async def compare_traces(trace_id1, trace_id2):
    storage = SQLiteTraceStorage()

    trace1 = await storage.get_trace(trace_id1)
    trace2 = await storage.get_trace(trace_id2)

    print(f"Trace 1: {trace1.duration_ms:.2f}ms")
    print(f"Trace 2: {trace2.duration_ms:.2f}ms")
    print(f"Difference: {abs(trace1.duration_ms - trace2.duration_ms):.2f}ms")

    # Compare span counts
    print(f"Spans: {trace1.span_count} vs {trace2.span_count}")
```

## 🔧 Configuration

### Basic Configuration

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

    # Optional: Extended telemetry
    telemetry_capture_state_dict=True,
    telemetry_capture_platform=True,
    telemetry_capture_tool_call_responses=True,
)
```

## 📊 Query Examples

### Filter by Workflow

```python
params = TraceQueryParams(
    workflow_name="MyWorkflow",
    limit=100
)
traces = await storage.list_traces(params)
```

### Filter by Duration

```python
# Slow traces (> 1s)
params = TraceQueryParams(min_duration_ms=1000)

# Fast traces (< 100ms)
params = TraceQueryParams(max_duration_ms=100)
```

### Filter by Errors

```python
# Only errors
params = TraceQueryParams(has_errors=True)

# No errors
params = TraceQueryParams(has_errors=False)
```

### Time Range

```python
from datetime import datetime, timedelta

now = datetime.now()
yesterday = now - timedelta(days=1)

params = TraceQueryParams(
    start_time=yesterday,
    end_time=now
)
```

### Pagination

```python
# First page
params = TraceQueryParams(limit=20, offset=0)

# Second page
params = TraceQueryParams(limit=20, offset=20)
```

## 🎨 Visualization

### Span Tree

```python
trace = await storage.get_trace(trace_id)
tree = trace.build_span_tree()

def print_tree(node, depth=0):
    span = node["span"]
    print("  " * depth + f"{span.name} ({span.duration_ms:.2f}ms)")
    for child in node["children"]:
        print_tree(child, depth + 1)

print_tree(tree)
```

Output:
```
Workflow (1234.5ms)
  Module A (800.2ms)
    Tool Call 1 (400.1ms)
    Tool Call 2 (350.0ms)
  Module B (400.0ms)
```

## 🔍 CLI Tips

### Pretty Stats

```bash
msgtrace stats
```

```
📊 msgtrace Statistics
========================================
Total traces: 42
Traces with errors: 3
Error rate: 7.14%
Database: msgtrace.db
Database size: 1.23 MB
```

### List with Details

```bash
msgtrace list --limit 5
```

```
🔍 Recent Traces
========================================

✅ abc123def456...
   Workflow: sentiment_analyzer
   Duration: 234.56ms
   Spans: 5 | Errors: 0

❌ def456abc789...
   Workflow: agent_workflow
   Duration: 1234.56ms
   Spans: 15 | Errors: 2
```

### Show Full Trace

```bash
msgtrace show abc123def456
```

## 🐛 Troubleshooting

### No traces appearing?

1. Check server is running:
```bash
curl http://localhost:4321/health
```

2. Check msgflux configuration:
```python
from msgflux.envs import envs
print(envs.telemetry_requires_trace)  # Should be True
print(envs.telemetry_otlp_endpoint)    # Should be correct
```

3. Check server logs

### Database locked?

```python
# Make sure to close connections
await storage.close()
```

### Port already in use?

```bash
# Use different port
msgtrace start --port 4322
```

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Examples**: Check `examples/` directory
- **API Docs**: `http://localhost:4321/docs`
- **Project Overview**: See `PROJECT_OVERVIEW.md`

## 🎉 You're Ready!

Start tracing your msgflux workflows and gain deep insights into your AI systems!

```python
from msgtrace.integration import quick_start

observer = quick_start()
# That's it! Start building amazing AI systems with full observability!
```
