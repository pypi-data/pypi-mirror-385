# msgtrace Frontend

A modern, feature-rich web UI for visualizing and analyzing msgflux trace data.

## Features

- **Dashboard**: Overview of trace statistics and recent traces
- **Trace List**: Browse and search traces with advanced filtering
- **Trace Details**: Detailed view with:
  - Timeline visualization
  - Span tree (hierarchical view)
  - Token usage and cost tracking
  - Error highlighting
  - Span details modal

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **TanStack Query** - Data fetching
- **React Router** - Navigation
- **Recharts** - Charts (ready for future use)
- **Lucide React** - Icons

## Development

```bash
# Install dependencies
npm install

# Start development server (proxies API to localhost:4321)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/       # Reusable components
│   ├── Layout.tsx
│   ├── Card.tsx
│   ├── Stat.tsx
│   ├── SpanTree.tsx
│   ├── Timeline.tsx
│   └── SpanDetails.tsx
├── views/           # Page components
│   ├── Dashboard.tsx
│   ├── TraceList.tsx
│   └── TraceDetail.tsx
├── hooks/           # Custom React hooks
│   └── useTraces.ts
├── lib/             # Utilities
│   ├── api.ts
│   └── utils.ts
├── types/           # TypeScript types
│   └── trace.ts
├── App.tsx          # Main app component
├── main.tsx         # App entry point
└── index.css        # Global styles
```

## API Integration

The frontend expects the msgtrace backend to be running on `http://localhost:4321`. All API calls are proxied through Vite during development.

### API Endpoints Used

- `GET /api/v1/traces` - List traces
- `GET /api/v1/traces/:id` - Get trace details
- `GET /api/v1/traces/:id/tree` - Get span tree
- `DELETE /api/v1/traces/:id` - Delete trace
- `GET /api/v1/stats` - Get statistics

## Token and Cost Tracking

The UI automatically displays token usage and costs when available in span attributes:

- `llm.usage.prompt_tokens`
- `llm.usage.completion_tokens`
- `llm.usage.total_tokens`
- `llm.cost.input`
- `llm.cost.output`
- `llm.cost.total`
- `llm.model`

## Features

### Timeline View

- Visualizes span execution over time
- Shows concurrent operations
- Hover to see span details
- Click to open detailed view

### Tree View

- Hierarchical span organization
- Auto-expands first 2 levels
- Color-coded by status (success/error)
- Shows duration and span kind

### Span Details Modal

- Complete span information
- Token usage metrics
- Cost breakdown
- Events timeline
- Attributes and metadata

### Filtering

- Search by trace ID, workflow, or service
- Filter by duration range
- Filter by error status
- Filter by workflow name

## Deployment

```bash
# Build the production bundle
npm run build

# The dist/ directory contains the static files
# Serve with any static file server
```

## Integration with msgtrace Backend

The frontend is designed to work seamlessly with the msgtrace backend. To run the complete stack:

1. Start the msgtrace backend:
   ```bash
   msgtrace start --port 4321
   ```

2. Start the frontend dev server:
   ```bash
   cd src/msgtrace/frontend
   npm run dev
   ```

3. Open http://localhost:3000

## Future Enhancements

- Real-time trace updates via WebSocket
- Trace comparison view
- Saved queries and filters
- Export traces to various formats
- Gantt chart visualization
- Flame graph for performance analysis
- Advanced search with query language
