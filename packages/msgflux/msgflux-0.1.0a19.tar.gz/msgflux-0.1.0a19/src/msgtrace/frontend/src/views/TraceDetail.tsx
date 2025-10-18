import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Clock, Activity, AlertCircle, Layers, Download, FileJson, FileSpreadsheet } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import SpanTree from '@/components/SpanTree'
import Timeline from '@/components/Timeline'
import SpanDetails from '@/components/SpanDetails'
import { useTrace, useTraceTree } from '@/hooks/useTraces'
import { formatDuration, getTraceDurationMs } from '@/types/trace'
import { exportToJSON, exportTraceDetailsToCSV, generateFilename } from '@/lib/export'
import { Tooltip } from '@/components/Tooltip'
import type { Span } from '@/types/trace'

export default function TraceDetail() {
  const { traceId } = useParams<{ traceId: string }>()
  const navigate = useNavigate()
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null)
  const [view, setView] = useState<'tree' | 'timeline'>('tree')
  const [showExportMenu, setShowExportMenu] = useState(false)

  const { data: trace, isLoading, error } = useTrace(traceId!)
  const { data: tree } = useTraceTree(traceId!)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading trace...</div>
      </div>
    )
  }

  if (error || !trace) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/traces')}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to traces
        </button>
        <Card>
          <CardContent className="py-12 text-center text-red-400">
            {error?.message || 'Trace not found'}
          </CardContent>
        </Card>
      </div>
    )
  }

  const duration = getTraceDurationMs(trace)
  const errorSpans = trace.spans.filter(s => s.status?.status_code === 'ERROR')

  // Calculate total tokens and costs
  const totalTokens = {
    input: 0,
    output: 0,
    total: 0,
  }
  const totalCost = {
    input: 0,
    output: 0,
    total: 0,
  }

  trace.spans.forEach(span => {
    const inputTokens = span.attributes?.['llm.usage.prompt_tokens'] as number | undefined
    const outputTokens = span.attributes?.['llm.usage.completion_tokens'] as number | undefined
    const tokens = span.attributes?.['llm.usage.total_tokens'] as number | undefined

    const inputCost = span.attributes?.['llm.cost.input'] as number | undefined
    const outputCost = span.attributes?.['llm.cost.output'] as number | undefined
    const cost = span.attributes?.['llm.cost.total'] as number | undefined

    if (inputTokens) totalTokens.input += inputTokens
    if (outputTokens) totalTokens.output += outputTokens
    if (tokens) totalTokens.total += tokens

    if (inputCost) totalCost.input += inputCost
    if (outputCost) totalCost.output += outputCost
    if (cost) totalCost.total += cost
  })

  const handleExportJSON = () => {
    const filename = generateFilename(`trace_${traceId}`, 'json')
    exportToJSON(trace, filename)
    setShowExportMenu(false)
  }

  const handleExportCSV = () => {
    const filename = generateFilename(`trace_${traceId}`, 'csv')
    exportTraceDetailsToCSV(trace, filename)
    setShowExportMenu(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <button
            onClick={() => navigate('/traces')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to traces
          </button>
          <h1 className="text-3xl font-bold text-white truncate">
            {trace.workflow_name || 'Trace Details'}
          </h1>
          <p className="text-sm text-gray-400 font-mono mt-2">{trace.trace_id}</p>
        </div>
        <div className="relative">
          <Tooltip content="Export trace">
            <button
              onClick={() => setShowExportMenu(!showExportMenu)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </Tooltip>
          {showExportMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10">
              <button
                onClick={handleExportJSON}
                className="w-full px-4 py-2 text-left hover:bg-gray-700 transition-colors flex items-center gap-2 text-white"
              >
                <FileJson className="w-4 h-4" />
                Export as JSON
              </button>
              <button
                onClick={handleExportCSV}
                className="w-full px-4 py-2 text-left hover:bg-gray-700 transition-colors flex items-center gap-2 text-white border-t border-gray-700"
              >
                <FileSpreadsheet className="w-4 h-4" />
                Export as CSV
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Duration</p>
              <p className="text-2xl font-bold text-white mt-1">{formatDuration(duration)}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary-500/10">
              <Clock className="w-6 h-6 text-primary-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Spans</p>
              <p className="text-2xl font-bold text-white mt-1">{trace.spans.length}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary-500/10">
              <Layers className="w-6 h-6 text-primary-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Errors</p>
              <p className="text-2xl font-bold text-white mt-1">{errorSpans.length}</p>
            </div>
            <div className="p-3 rounded-lg bg-red-500/10">
              <AlertCircle className="w-6 h-6 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Cost</p>
              <p className="text-2xl font-bold text-green-400 mt-1">
                {totalCost.total > 0 ? `$${totalCost.total.toFixed(6)}` : 'N/A'}
              </p>
              {totalTokens.total > 0 && (
                <p className="text-xs text-gray-400 mt-1">
                  {totalTokens.total.toLocaleString()} tokens
                </p>
              )}
            </div>
            <div className="p-3 rounded-lg bg-green-500/10">
              <Activity className="w-6 h-6 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Metadata */}
      {(trace.service_name || Object.keys(trace.metadata).length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle>Metadata</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              {trace.service_name && (
                <div>
                  <div className="text-gray-400 mb-1">Service</div>
                  <div className="text-white font-mono">{trace.service_name}</div>
                </div>
              )}
              {trace.workflow_name && (
                <div>
                  <div className="text-gray-400 mb-1">Workflow</div>
                  <div className="text-white font-mono">{trace.workflow_name}</div>
                </div>
              )}
              <div>
                <div className="text-gray-400 mb-1">Start Time</div>
                <div className="text-white font-mono">
                  {new Date(trace.start_time / 1_000_000).toLocaleString()}
                </div>
              </div>
              {Object.entries(trace.metadata).map(([key, value]) => (
                <div key={key}>
                  <div className="text-gray-400 mb-1">{key}</div>
                  <div className="text-white font-mono truncate" title={String(value)}>
                    {String(value)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* View Toggle */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Trace Visualization</CardTitle>
            <div className="flex gap-2">
              <button
                onClick={() => setView('tree')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  view === 'tree'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                Tree View
              </button>
              <button
                onClick={() => setView('timeline')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  view === 'timeline'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white'
                }`}
              >
                Timeline
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {view === 'tree' && tree ? (
            <SpanTree tree={tree} onSpanClick={setSelectedSpan} />
          ) : view === 'timeline' ? (
            <Timeline trace={trace} onSpanClick={setSelectedSpan} />
          ) : (
            <div className="text-center py-8 text-gray-400">
              Loading visualization...
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Spans (if any) */}
      {errorSpans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-5 h-5" />
              Errors ({errorSpans.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {errorSpans.map(span => (
                <button
                  key={span.span_id}
                  onClick={() => setSelectedSpan(span)}
                  className="w-full text-left p-4 bg-red-500/5 border border-red-500/20 rounded-lg hover:bg-red-500/10 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-red-300 truncate">{span.name}</h4>
                      {span.status?.description && (
                        <p className="text-sm text-gray-400 mt-1">{span.status.description}</p>
                      )}
                      <p className="text-xs text-gray-500 font-mono mt-1">{span.span_id}</p>
                    </div>
                    <span className="text-xs text-gray-400 flex-shrink-0 ml-4">
                      {formatDuration(getTraceDurationMs({ start_time: span.start_time, end_time: span.end_time } as any))}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Span Details Modal */}
      <SpanDetails span={selectedSpan} onClose={() => setSelectedSpan(null)} />
    </div>
  )
}
