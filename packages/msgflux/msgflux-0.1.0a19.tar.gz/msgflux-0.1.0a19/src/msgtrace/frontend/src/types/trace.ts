export interface SpanStatus {
  status_code: 'OK' | 'ERROR' | 'UNSET'
  description?: string
}

export interface SpanEvent {
  name: string
  timestamp: number
  attributes: Record<string, any>
}

export interface Span {
  span_id: string
  trace_id: string
  parent_span_id?: string
  name: string
  kind: 'INTERNAL' | 'SERVER' | 'CLIENT' | 'PRODUCER' | 'CONSUMER'
  start_time: number
  end_time: number
  attributes: Record<string, any>
  events: SpanEvent[]
  status?: SpanStatus
  resource_attributes: Record<string, any>
}

export interface Trace {
  trace_id: string
  spans: Span[]
  start_time: number
  end_time: number
  root_span_id?: string
  service_name?: string
  workflow_name?: string
  metadata: Record<string, any>
}

export interface TraceSummary {
  trace_id: string
  start_time: number
  end_time: number
  duration_ms: number
  span_count: number
  error_count: number
  service_name?: string
  workflow_name?: string
  root_span_name?: string
}

export interface TraceQueryParams {
  service_name?: string
  workflow_name?: string
  min_duration_ms?: number
  max_duration_ms?: number
  has_errors?: boolean
  start_time?: string
  end_time?: string
  limit?: number
  offset?: number
}

export interface TraceListResponse {
  traces: TraceSummary[]
  total: number
  limit: number
  offset: number
}

export interface SpanTreeNode {
  span: Span
  children: SpanTreeNode[]
}

export interface Stats {
  total_traces: number
  traces_with_errors: number
  error_rate: number
}

// Helper functions
export function getSpanDurationMs(span: Span): number {
  return (span.end_time - span.start_time) / 1_000_000
}

export function getTraceDurationMs(trace: Trace): number {
  return (trace.end_time - trace.start_time) / 1_000_000
}

export function isSpanError(span: Span): boolean {
  return span.status?.status_code === 'ERROR'
}

export function formatDuration(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(2)}μs`
  if (ms < 1000) return `${ms.toFixed(2)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`
  return `${(ms / 60000).toFixed(2)}m`
}

export function formatTimestamp(ns: number): string {
  return new Date(ns / 1_000_000).toISOString()
}
