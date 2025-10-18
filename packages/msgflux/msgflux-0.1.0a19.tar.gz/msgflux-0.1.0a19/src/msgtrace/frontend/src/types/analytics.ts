/**
 * Analytics Types for msgtrace Frontend
 */

export interface LatencyPercentiles {
  p50: number
  p95: number
  p99: number
  count: number
  mean: number
  min: number
  max: number
  time_window_hours: number
  workflow_name?: string
  service_name?: string
}

export interface TimeSeriesBucket {
  timestamp: number
  time: string
  count: number
  p50?: number
  p95?: number
  mean?: number
  min?: number
  max?: number
  rate_per_minute?: number
  total_traces?: number
  error_traces?: number
  error_rate?: number
  success_rate?: number
}

export interface LatencyTimeSeries {
  buckets: TimeSeriesBucket[]
  total_traces: number
  time_window_hours: number
  bucket_minutes: number
}

export interface ErrorTimeSeries {
  buckets: TimeSeriesBucket[]
  total_traces: number
  time_window_hours: number
  bucket_minutes: number
}

export interface ThroughputTimeSeries {
  buckets: TimeSeriesBucket[]
  total_traces: number
  time_window_hours: number
  bucket_minutes: number
}

export interface WorkflowMetrics {
  workflow_name: string
  count: number
  p50: number
  p95: number
  mean: number
  error_count: number
  error_rate: number
}

export interface WorkflowComparison {
  workflows: WorkflowMetrics[]
  total_workflows: number
  time_window_hours: number
}

// Helper functions
export function formatLatency(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}µs`
  if (ms < 1000) return `${ms.toFixed(0)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`
  return `${(ms / 60000).toFixed(2)}m`
}

export function formatPercentile(value: number): string {
  return `${value.toFixed(2)}ms`
}

export function formatRate(rate: number): string {
  return `${rate.toFixed(2)}%`
}

export function formatThroughput(count: number, minutes: number): string {
  const perMinute = count / minutes
  if (perMinute < 1) return `${(perMinute * 60).toFixed(1)}/hour`
  return `${perMinute.toFixed(1)}/min`
}
