import type { Trace, TraceSummary } from '@/types/trace'

export function exportToJSON(data: Trace | Trace[] | TraceSummary[], filename: string): void {
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  downloadBlob(blob, filename)
}

export function exportToCSV(traces: TraceSummary[], filename: string): void {
  // CSV headers
  const headers = [
    'Trace ID',
    'Workflow Name',
    'Service Name',
    'Duration (ms)',
    'Span Count',
    'Error Count',
    'Start Time',
    'End Time',
  ]

  // CSV rows
  const rows = traces.map(trace => [
    trace.trace_id,
    trace.workflow_name || '',
    trace.service_name || '',
    trace.duration_ms.toFixed(2),
    trace.span_count.toString(),
    trace.error_count.toString(),
    new Date(trace.start_time / 1_000_000).toISOString(),
    new Date(trace.end_time / 1_000_000).toISOString(),
  ])

  // Build CSV content
  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(escapeCSV).join(',')),
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  downloadBlob(blob, filename)
}

export function exportTraceDetailsToCSV(trace: Trace, filename: string): void {
  // CSV headers for spans
  const headers = [
    'Span ID',
    'Trace ID',
    'Parent Span ID',
    'Name',
    'Kind',
    'Duration (ms)',
    'Status',
    'Start Time',
    'End Time',
  ]

  // CSV rows
  const rows = trace.spans.map(span => {
    const durationMs = (span.end_time - span.start_time) / 1_000_000
    return [
      span.span_id,
      span.trace_id,
      span.parent_span_id || '',
      span.name,
      span.kind,
      durationMs.toFixed(2),
      span.status?.status_code || 'UNSET',
      new Date(span.start_time / 1_000_000).toISOString(),
      new Date(span.end_time / 1_000_000).toISOString(),
    ]
  })

  // Build CSV content
  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(escapeCSV).join(',')),
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  downloadBlob(blob, filename)
}

function escapeCSV(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`
  }
  return value
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function generateFilename(prefix: string, extension: string): string {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
  return `${prefix}_${timestamp}.${extension}`
}
