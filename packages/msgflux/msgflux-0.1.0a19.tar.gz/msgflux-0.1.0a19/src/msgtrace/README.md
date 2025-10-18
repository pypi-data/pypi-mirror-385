# msgtrace

**Trace visualization and observability for msgflux**

msgtrace is a lightweight, self-hosted observability platform designed specifically for msgflux AI systems. It captures, stores, and visualizes OpenTelemetry traces from your msgflux workflows, providing deep insights into execution flow, performance, and errors.

## Features

- 🔍 **Trace Collection**: OTLP-compatible collector receives traces from msgflux
- 💾 **SQLite Storage**: Simple, file-based storage (PostgreSQL/ClickHouse ready for scale)
- 🚀 **REST API**: Query and analyze traces programmatically
- 📊 **Rich Insights**: Duration, span counts, error tracking, and more
- 🎯 **Zero Config**: One-line setup with automatic msgflux integration
- 🌐 **Self-Hosted**: Your data stays local, no external dependencies

## Quick Start

### Installation

```bash
pip install msgtrace
```

### Option 1: Quick Start (Easiest)

```python
from msgtrace.integration import quick_start

# Start everything with one line
observer = quick_start(port=4321)

# Your msgflux code here
from msgflux.nn import Predictor
predictor = Predictor(...)
result = predictor(message)

# Stop when done
observer.stop()
```

### Option 2: Manual Setup

```python
from msgtrace import start_observer, configure_msgflux_telemetry

# Start the observer
observer = start_observer(port=4321)

# Configure msgflux
configure_msgflux_telemetry(
    server=observer,
    enable_state_dict=True,  # Capture module states
    enable_platform=True,     # Capture platform info
)

# Your msgflux code here
# ...

observer.stop()
```

### Option 3: CLI

```bash
# Start the server
msgtrace start --port 4321

# In your Python code, configure msgflux
from msgtrace import configure_msgflux_telemetry
configure_msgflux_telemetry(port=4321)

# View stats
msgtrace stats

# List recent traces
msgtrace list --limit 20

# Show specific trace
msgtrace show abc123def456
```

## API Usage

### REST API Endpoints

Once the server is running, you can access:

- **API Documentation**: `http://localhost:4321/docs`
- **Health Check**: `http://localhost:4321/health`
- **List Traces**: `GET /api/v1/traces`
- **Get Trace**: `GET /api/v1/traces/{trace_id}`
- **Get Trace Tree**: `GET /api/v1/traces/{trace_id}/tree`
- **Stats**: `GET /api/v1/stats`
- **OTLP Export**: `POST /api/v1/traces/export`

### Python API

```python
from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams

# Query traces
storage = SQLiteTraceStorage("msgtrace.db")

# List traces
params = TraceQueryParams(
    workflow_name="MyWorkflow",
    has_errors=False,
    limit=10
)
traces = await storage.list_traces(params)

# Get specific trace
trace = await storage.get_trace(trace_id)

# Build span tree for visualization
tree = trace.build_span_tree()

await storage.close()
```

## Configuration

### MsgTrace Server

```python
from msgtrace.core.config import MsgTraceConfig

config = MsgTraceConfig(
    host="0.0.0.0",
    port=4321,
    db_path="msgtrace.db",
    cors_origins=["*"],
    queue_size=1000
)

observer = start_observer(config=config)
```

### msgflux Integration

```python
from msgflux import set_envs

set_envs(
    telemetry_requires_trace=True,
    telemetry_span_exporter_type="otlp",
    telemetry_otlp_endpoint="http://localhost:4321/api/v1/traces/export",
    telemetry_capture_state_dict=True,      # Capture module states
    telemetry_capture_platform=True,         # Capture platform info
    telemetry_capture_tool_call_responses=True,  # Capture tool outputs
    telemetry_capture_agent_prepare_model_execution=False,  # Agent internals
)
```

## CLI Commands

```bash
# Start server
msgtrace start [OPTIONS]
  --host TEXT       Host to bind to [default: 0.0.0.0]
  --port INTEGER    Port to bind to [default: 4321]
  --db-path TEXT    Database path [default: msgtrace.db]
  --reload          Enable auto-reload for development

# View statistics
msgtrace stats [OPTIONS]
  --db-path TEXT    Database path [default: msgtrace.db]

# List traces
msgtrace list [OPTIONS]
  --db-path TEXT    Database path [default: msgtrace.db]
  --limit INTEGER   Number of traces [default: 10]

# Show trace details
msgtrace show TRACE_ID [OPTIONS]
  --db-path TEXT    Database path [default: msgtrace.db]

# Clear database
msgtrace clear [OPTIONS]
  --db-path TEXT    Database path [default: msgtrace.db]
```

## Examples

### Basic Workflow Tracing

```python
from msgtrace.integration import quick_start
from msgflux.nn import Predictor
from msgflux.message import Message

# Setup
observer = quick_start()

# Create a predictor
predictor = Predictor(
    name="sentiment_analyzer",
    task_template="Analyze sentiment: {text}",
    generation_schema={"sentiment": str, "confidence": float}
)

# Run prediction
message = Message(inputs={"text": "I love this product!"})
result = predictor(message)

print(result)

# Stop observer
observer.stop()
```

### Agent Workflow Tracing

```python
from msgtrace.integration import quick_start
from msgflux.nn import Agent, Tool

# Setup with extended telemetry
observer = quick_start(enable_state_dict=True)

# Define tools
@Tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

# Create agent
agent = Agent(
    name="research_agent",
    tools=[search_web],
    system_prompt="You are a helpful research assistant."
)

# Run agent
message = Message(inputs={"task": "Research AI trends in 2024"})
result = agent(message)

# Traces are automatically captured!

observer.stop()
```

### Querying Traces

```python
import asyncio
from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams

async def analyze_traces():
    storage = SQLiteTraceStorage("msgtrace.db")

    # Find slow traces
    slow_traces = await storage.list_traces(
        TraceQueryParams(min_duration_ms=1000, limit=10)
    )

    print("Slow traces:")
    for trace in slow_traces:
        print(f"  {trace.workflow_name}: {trace.duration_ms:.2f}ms")

    # Find error traces
    error_traces = await storage.list_traces(
        TraceQueryParams(has_errors=True, limit=10)
    )

    print(f"\nError traces: {len(error_traces)}")

    await storage.close()

asyncio.run(analyze_traces())
```

## Architecture

```
msgtrace/
├── backend/              # Backend services
│   ├── api/             # FastAPI REST API
│   ├── collectors/      # OTLP trace collector
│   ├── services/        # Business logic
│   └── storage/         # Storage layer (SQLite)
├── core/                # Core library
│   ├── models/          # Data models (Trace, Span)
│   ├── parsers/         # OTLP parser
│   └── analyzers/       # Trace analysis
└── cli/                 # Command-line interface
```

## Data Models

### Trace
- `trace_id`: Unique identifier
- `spans`: List of all spans
- `start_time` / `end_time`: Timestamps (nanoseconds)
- `duration_ms`: Total duration
- `workflow_name`: Root workflow name
- `error_count`: Number of failed spans

### Span
- `span_id`: Unique identifier
- `trace_id`: Parent trace ID
- `parent_span_id`: Parent span ID (if nested)
- `name`: Span name (e.g., module name)
- `kind`: INTERNAL, SERVER, CLIENT, etc.
- `start_time` / `end_time`: Timestamps
- `attributes`: Custom key-value attributes
- `events`: List of events during span
- `status`: OK, ERROR, UNSET

## Storage

### SQLite (Default)
- Perfect for development and small-scale deployments
- File-based, no external dependencies
- Automatic schema initialization

### Future Support
- **PostgreSQL + TimescaleDB**: For production time-series workloads
- **ClickHouse**: For large-scale OLAP analytics

## Performance

msgtrace is designed to be lightweight with minimal overhead:

- **Async processing**: Non-blocking trace collection
- **Batching**: Efficient bulk operations
- **Queue-based**: Prevents blocking your application
- **Zero overhead when disabled**: No performance impact when telemetry is off

## Development

### Setup

```bash
cd src/msgtrace
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Run with Auto-reload

```bash
msgtrace start --reload
```

## Roadmap

### Phase 1 (MVP) ✅
- [x] OTLP collector
- [x] SQLite storage
- [x] REST API
- [x] CLI tool
- [x] msgflux integration

### Phase 2 (Advanced Features)
- [ ] Web UI for visualization
- [ ] Timeline and tree views
- [ ] Flame graphs
- [ ] Search and filtering
- [ ] Comparison tools

### Phase 3 (Production)
- [ ] PostgreSQL/ClickHouse support
- [ ] Multi-tenancy
- [ ] Authentication
- [ ] Alerts and webhooks
- [ ] Grafana integration

## Contributing

Contributions are welcome! This project will be moved to its own repository soon.

## License

MIT License

## Links

- **Documentation**: Coming soon
- **GitHub**: Coming soon
- **msgflux**: https://github.com/msgflux/msgflux
