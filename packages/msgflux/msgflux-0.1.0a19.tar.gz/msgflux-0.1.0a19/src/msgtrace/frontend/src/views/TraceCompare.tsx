import { useSearchParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import { useTrace } from '@/hooks/useTraces'
import { formatDuration, getTraceDurationMs } from '@/types/trace'

export default function TraceCompare() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const trace1Id = searchParams.get('trace1')
  const trace2Id = searchParams.get('trace2')

  const { data: trace1, isLoading: loading1 } = useTrace(trace1Id || '')
  const { data: trace2, isLoading: loading2 } = useTrace(trace2Id || '')

  if (!trace1Id || !trace2Id) {
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
          <CardContent className="py-12 text-center text-gray-400">
            Please select two traces to compare
          </CardContent>
        </Card>
      </div>
    )
  }

  if (loading1 || loading2) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading traces...</div>
      </div>
    )
  }

  if (!trace1 || !trace2) {
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
            One or both traces not found
          </CardContent>
        </Card>
      </div>
    )
  }

  const duration1 = getTraceDurationMs(trace1)
  const duration2 = getTraceDurationMs(trace2)
  const durationDiff = duration2 - duration1
  const durationPercent = ((durationDiff / duration1) * 100).toFixed(1)

  const spanDiff = trace2.spans.length - trace1.spans.length
  const error1Count = trace1.spans.filter(s => s.status?.status_code === 'ERROR').length
  const error2Count = trace2.spans.filter(s => s.status?.status_code === 'ERROR').length
  const errorDiff = error2Count - error1Count

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/traces')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to traces
          </button>
          <h1 className="text-3xl font-bold text-white">Compare Traces</h1>
        </div>
      </div>

      {/* Comparison Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Duration Difference</p>
              <p className="text-2xl font-bold text-white mt-1">
                {formatDuration(Math.abs(durationDiff))}
              </p>
              <div className="flex items-center gap-1 mt-1">
                {durationDiff > 0 ? (
                  <>
                    <TrendingUp className="w-4 h-4 text-red-400" />
                    <span className="text-sm text-red-400">+{durationPercent}% slower</span>
                  </>
                ) : durationDiff < 0 ? (
                  <>
                    <TrendingDown className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-green-400">{durationPercent}% faster</span>
                  </>
                ) : (
                  <span className="text-sm text-gray-400">Same</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Span Count Difference</p>
              <p className="text-2xl font-bold text-white mt-1">
                {Math.abs(spanDiff)}
              </p>
              <span className={`text-sm ${spanDiff > 0 ? 'text-primary-400' : spanDiff < 0 ? 'text-gray-400' : 'text-gray-400'}`}>
                {spanDiff > 0 ? `+${spanDiff} more` : spanDiff < 0 ? `${spanDiff} fewer` : 'Same'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Error Difference</p>
              <p className="text-2xl font-bold text-white mt-1">
                {Math.abs(errorDiff)}
              </p>
              <span className={`text-sm ${errorDiff > 0 ? 'text-red-400' : errorDiff < 0 ? 'text-green-400' : 'text-gray-400'}`}>
                {errorDiff > 0 ? `+${errorDiff} more` : errorDiff < 0 ? `${Math.abs(errorDiff)} fewer` : 'Same'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Side by Side Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trace 1 */}
        <Card>
          <CardHeader className="border-b border-primary-500/20 bg-primary-500/5">
            <div className="flex items-center justify-between">
              <CardTitle className="text-primary-400">Trace 1</CardTitle>
              <button
                onClick={() => navigate(`/traces/${trace1.trace_id}`)}
                className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
              >
                View Details <ArrowRight className="inline w-4 h-4" />
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm text-gray-400 mb-1">Workflow</div>
              <div className="text-white">{trace1.workflow_name || 'Unknown'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Trace ID</div>
              <div className="text-xs text-gray-400 font-mono break-all">{trace1.trace_id}</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-400 mb-1">Duration</div>
                <div className="text-lg font-semibold text-white">{formatDuration(duration1)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Spans</div>
                <div className="text-lg font-semibold text-white">{trace1.spans.length}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Errors</div>
                <div className="text-lg font-semibold text-white">{error1Count}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Started</div>
                <div className="text-sm text-white">
                  {new Date(trace1.start_time / 1_000_000).toLocaleString()}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Trace 2 */}
        <Card>
          <CardHeader className="border-b border-green-500/20 bg-green-500/5">
            <div className="flex items-center justify-between">
              <CardTitle className="text-green-400">Trace 2</CardTitle>
              <button
                onClick={() => navigate(`/traces/${trace2.trace_id}`)}
                className="text-sm text-green-400 hover:text-green-300 transition-colors"
              >
                View Details <ArrowRight className="inline w-4 h-4" />
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm text-gray-400 mb-1">Workflow</div>
              <div className="text-white">{trace2.workflow_name || 'Unknown'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Trace ID</div>
              <div className="text-xs text-gray-400 font-mono break-all">{trace2.trace_id}</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-400 mb-1">Duration</div>
                <div className="text-lg font-semibold text-white">{formatDuration(duration2)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Spans</div>
                <div className="text-lg font-semibold text-white">{trace2.spans.length}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Errors</div>
                <div className="text-lg font-semibold text-white">{error2Count}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">Started</div>
                <div className="text-sm text-white">
                  {new Date(trace2.start_time / 1_000_000).toLocaleString()}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Span Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Span Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">Span Name</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Trace 1</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Trace 2</th>
                  <th className="text-right py-3 px-4 text-gray-400 font-medium">Diff</th>
                </tr>
              </thead>
              <tbody>
                {trace1.spans.map((span1) => {
                  const span2 = trace2.spans.find(s => s.name === span1.name)
                  const duration1Ms = (span1.end_time - span1.start_time) / 1_000_000
                  const duration2Ms = span2 ? (span2.end_time - span2.start_time) / 1_000_000 : 0
                  const diff = duration2Ms - duration1Ms

                  return (
                    <tr key={span1.span_id} className="border-b border-gray-800/50">
                      <td className="py-3 px-4 text-white">{span1.name}</td>
                      <td className="py-3 px-4 text-right text-gray-300">{formatDuration(duration1Ms)}</td>
                      <td className="py-3 px-4 text-right text-gray-300">
                        {span2 ? formatDuration(duration2Ms) : '-'}
                      </td>
                      <td className={`py-3 px-4 text-right font-medium ${
                        !span2 ? 'text-gray-500' :
                        diff > 0 ? 'text-red-400' :
                        diff < 0 ? 'text-green-400' :
                        'text-gray-400'
                      }`}>
                        {!span2 ? 'Not found' :
                         diff > 0 ? `+${formatDuration(diff)}` :
                         diff < 0 ? formatDuration(diff) :
                         'Same'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
