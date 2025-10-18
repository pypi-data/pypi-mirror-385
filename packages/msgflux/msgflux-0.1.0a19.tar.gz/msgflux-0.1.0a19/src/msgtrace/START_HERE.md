# 🚀 msgtrace - START HERE

Welcome! This is your starting point for using msgtrace.

---

## ⚡ 5-Minute Quick Start

### Step 1: Build the Frontend

```bash
cd src/msgtrace/frontend
npm install
npm run build
cd ../../..
```

### Step 2: Start the Server

```bash
msgtrace start --port 4321
```

### Step 3: Open Your Browser

```
http://localhost:4321
```

🎉 **Done!** You now have a complete trace visualization system running.

---

## 🎯 What Can You Do Now?

### 1. Generate Example Traces

```bash
python -m msgtrace.examples.e2e_example
```

This will:
- Start capturing traces automatically
- Run sample workflows
- Show you how to query traces
- Display token usage and costs

### 2. Explore the Web UI

Open http://localhost:4321 and check out:

- **Dashboard** (`/dashboard`)
  - Live statistics
  - Recent traces
  - Error monitoring

- **Trace List** (`/traces`)
  - Search and filter
  - Sort by duration, errors, etc.
  - Delete traces

- **Trace Details** (click any trace)
  - Timeline visualization
  - Span tree (hierarchical view)
  - Token usage and costs
  - Error details

### 3. Use Your Own Workflows

```python
from msgtrace.integration import quick_start

# Start msgtrace
observer = quick_start(port=4321)

# Your msgflux code here
from msgflux.nn import Predictor
from msgflux.message import Message

predictor = Predictor(
    name="my_predictor",
    task_template="Analyze: {text}"
)

result = predictor(Message(inputs={"text": "Hello!"}))

# Traces are automatically captured!
# View them at http://localhost:4321
```

---

## 📚 Next Steps

### Learn More

| Document | When to Read |
|----------|-------------|
| `QUICKSTART.md` | Want a 60-second overview? |
| `README.md` | Want complete documentation? |
| `examples/README.md` | Want to see more examples? |
| `DEPLOYMENT.md` | Ready to deploy to production? |
| `INTEGRATION_COMPLETE.md` | Want to know what's been built? |

### Try Examples

```bash
# Basic workflow tracing
python -m msgtrace.examples.basic_tracing

# Agent workflow tracing
python -m msgtrace.examples.agent_tracing

# Query and analyze traces
python -m msgtrace.examples.query_traces

# Complete end-to-end demo ⭐
python -m msgtrace.examples.e2e_example
```

### Deploy to Production

```bash
# Using Docker
cd src/msgtrace
docker-compose up -d

# Using systemd
sudo systemctl enable msgtrace
sudo systemctl start msgtrace
```

---

## 🔧 Common Tasks

### View Traces in CLI

```bash
# Show statistics
msgtrace stats

# List recent traces
msgtrace list --limit 10

# Show specific trace
msgtrace show <trace-id>

# Clear database
msgtrace clear
```

### Query via API

```bash
# List traces
curl http://localhost:4321/api/v1/traces

# Get specific trace
curl http://localhost:4321/api/v1/traces/<trace-id>

# Get statistics
curl http://localhost:4321/api/v1/stats

# API documentation
open http://localhost:4321/docs
```

### Query via Python

```python
import asyncio
from msgtrace.backend.storage import SQLiteTraceStorage
from msgtrace.core.models import TraceQueryParams

async def get_traces():
    storage = SQLiteTraceStorage("msgtrace.db")

    # List traces
    traces = await storage.list_traces(TraceQueryParams(limit=10))

    # Get detailed trace
    trace = await storage.get_trace(traces[0].trace_id)

    await storage.close()

asyncio.run(get_traces())
```

---

## 💡 Tips

1. **Keep the server running** - Traces are captured automatically
2. **Use the web UI** - It's the easiest way to explore traces
3. **Try the examples** - They show best practices
4. **Filter traces** - Use search to find what you need
5. **Check token costs** - Monitor LLM usage in the UI

---

## ❓ Troubleshooting

### "Frontend not showing"

```bash
# Rebuild frontend
cd src/msgtrace/frontend
npm run build

# Restart server
msgtrace start --port 4321
```

### "Port already in use"

```bash
# Use a different port
msgtrace start --port 4322
```

### "No traces appearing"

```bash
# Check health
curl http://localhost:4321/health

# Verify msgflux telemetry is enabled
# (examples do this automatically)
```

---

## 🎉 You're All Set!

msgtrace is now ready to capture and visualize your msgflux workflows.

**Next**: Run the complete example to see everything in action:

```bash
python -m msgtrace.examples.e2e_example
```

Then open http://localhost:4321 and explore! 🚀

---

## 📞 Need Help?

- **Examples**: `examples/README.md`
- **Full Docs**: `README.md`
- **Deployment**: `DEPLOYMENT.md`
- **API Reference**: http://localhost:4321/docs

Happy tracing! ✨
