import { X, Clock, Tag, Activity, AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from './Card'
import { formatDuration, formatTimestamp, getSpanDurationMs, isSpanError } from '@/types/trace'
import type { Span } from '@/types/trace'

interface SpanDetailsProps {
  span: Span | null
  onClose: () => void
}

export default function SpanDetails({ span, onClose }: SpanDetailsProps) {
  if (!span) return null

  const duration = getSpanDurationMs(span)
  const isError = isSpanError(span)

  // Extract token and cost information from attributes
  const tokens = {
    input: span.attributes?.['llm.usage.prompt_tokens'] as number | undefined,
    output: span.attributes?.['llm.usage.completion_tokens'] as number | undefined,
    total: span.attributes?.['llm.usage.total_tokens'] as number | undefined,
  }

  const cost = {
    input: span.attributes?.['llm.cost.input'] as number | undefined,
    output: span.attributes?.['llm.cost.output'] as number | undefined,
    total: span.attributes?.['llm.cost.total'] as number | undefined,
  }

  const model = span.attributes?.['llm.model'] as string | undefined

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader className="flex flex-row items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <CardTitle className="truncate">{span.name}</CardTitle>
              {isError && (
                <span className="px-2 py-0.5 text-xs font-medium rounded bg-red-500/20 text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Error
                </span>
              )}
            </div>
            <p className="text-xs text-gray-400 font-mono">{span.span_id}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
                <Clock className="w-4 h-4" />
                Duration
              </div>
              <p className="text-lg font-semibold text-white">{formatDuration(duration)}</p>
            </div>
            <div>
              <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
                <Tag className="w-4 h-4" />
                Kind
              </div>
              <p className="text-lg font-semibold text-white">{span.kind}</p>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Start Time</div>
              <p className="text-sm font-mono text-white">{formatTimestamp(span.start_time)}</p>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">End Time</div>
              <p className="text-sm font-mono text-white">{formatTimestamp(span.end_time)}</p>
            </div>
          </div>

          {/* LLM Info */}
          {model && (
            <div className="border-t border-gray-800 pt-6">
              <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4" />
                LLM Information
              </h4>
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Model</div>
                  <p className="text-sm font-mono text-white">{model}</p>
                </div>
                {(tokens.input || tokens.output || tokens.total) && (
                  <div className="grid grid-cols-3 gap-4">
                    {tokens.input && (
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Input Tokens</div>
                        <p className="text-lg font-semibold text-white">{tokens.input.toLocaleString()}</p>
                      </div>
                    )}
                    {tokens.output && (
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Output Tokens</div>
                        <p className="text-lg font-semibold text-white">{tokens.output.toLocaleString()}</p>
                      </div>
                    )}
                    {tokens.total && (
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Total Tokens</div>
                        <p className="text-lg font-semibold text-white">{tokens.total.toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                )}
                {(cost.input || cost.output || cost.total) && (
                  <div className="grid grid-cols-3 gap-4">
                    {cost.input && (
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Input Cost</div>
                        <p className="text-lg font-semibold text-green-400">${cost.input.toFixed(6)}</p>
                      </div>
                    )}
                    {cost.output && (
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Output Cost</div>
                        <p className="text-lg font-semibold text-green-400">${cost.output.toFixed(6)}</p>
                      </div>
                    )}
                    {cost.total && (
                      <div>
                        <div className="text-xs text-gray-400 mb-1">Total Cost</div>
                        <p className="text-lg font-semibold text-green-400">${cost.total.toFixed(6)}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Status */}
          {span.status && (
            <div className="border-t border-gray-800 pt-6">
              <h4 className="text-sm font-semibold text-white mb-3">Status</h4>
              <div className="space-y-2">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Code</div>
                  <p className={`text-sm font-mono ${isError ? 'text-red-400' : 'text-green-400'}`}>
                    {span.status.status_code}
                  </p>
                </div>
                {span.status.description && (
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Description</div>
                    <p className="text-sm text-white">{span.status.description}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Attributes */}
          {Object.keys(span.attributes).length > 0 && (
            <div className="border-t border-gray-800 pt-6">
              <h4 className="text-sm font-semibold text-white mb-3">Attributes</h4>
              <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-xs text-gray-300 font-mono">
                  {JSON.stringify(span.attributes, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Events */}
          {span.events.length > 0 && (
            <div className="border-t border-gray-800 pt-6">
              <h4 className="text-sm font-semibold text-white mb-3">
                Events ({span.events.length})
              </h4>
              <div className="space-y-2">
                {span.events.map((event, idx) => (
                  <div key={idx} className="bg-gray-900 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-white">{event.name}</span>
                      <span className="text-xs text-gray-400 font-mono">
                        {formatTimestamp(event.timestamp)}
                      </span>
                    </div>
                    {Object.keys(event.attributes).length > 0 && (
                      <pre className="text-xs text-gray-400 font-mono mt-2">
                        {JSON.stringify(event.attributes, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Resource Attributes */}
          {Object.keys(span.resource_attributes).length > 0 && (
            <div className="border-t border-gray-800 pt-6">
              <h4 className="text-sm font-semibold text-white mb-3">Resource Attributes</h4>
              <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-xs text-gray-300 font-mono">
                  {JSON.stringify(span.resource_attributes, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
