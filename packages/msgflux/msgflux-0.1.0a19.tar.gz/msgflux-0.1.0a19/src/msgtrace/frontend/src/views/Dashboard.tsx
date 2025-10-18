import { Activity, AlertCircle, Clock, TrendingUp } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import Stat from '@/components/Stat'
import { StatSkeleton, TraceListSkeleton } from '@/components/Skeleton'
import { ErrorState, EmptyState } from '@/components/ErrorState'
import { useStats, useTraces } from '@/hooks/useTraces'
import { formatDuration } from '@/types/trace'

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useStats()
  const { data: recentTraces, isLoading: tracesLoading, error: tracesError, refetch: refetchTraces } = useTraces({ limit: 10 })

  if (statsError || tracesError) {
    return (
      <ErrorState
        title="Failed to Load Dashboard"
        message={statsError?.message || tracesError?.message || 'An unexpected error occurred'}
        onRetry={() => {
          if (statsError) refetchStats()
          if (tracesError) refetchTraces()
        }}
      />
    )
  }

  if (statsLoading || tracesLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-2">Overview of your trace data</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <StatSkeleton key={i} />
          ))}
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Recent Traces</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <TraceListSkeleton />
          </CardContent>
        </Card>
      </div>
    )
  }

  const avgDuration = recentTraces?.traces.length
    ? recentTraces.traces.reduce((sum, t) => sum + t.duration_ms, 0) / recentTraces.traces.length
    : 0

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-2">Overview of your trace data</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Stat
          label="Total Traces"
          value={stats?.total_traces || 0}
          icon={Activity}
          tooltip="Total number of traces captured by msgtrace"
        />
        <Stat
          label="Errors"
          value={stats?.traces_with_errors || 0}
          icon={AlertCircle}
          tooltip="Number of traces that contain at least one error"
        />
        <Stat
          label="Error Rate"
          value={`${((stats?.error_rate || 0) * 100).toFixed(1)}%`}
          icon={TrendingUp}
          tooltip="Percentage of traces with errors"
        />
        <Stat
          label="Avg Duration"
          value={formatDuration(avgDuration)}
          icon={Clock}
          tooltip="Average execution time across all recent traces"
        />
      </div>

      {/* Recent Traces */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Traces</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {recentTraces?.traces.length === 0 ? (
            <div className="px-6 py-12">
              <EmptyState
                message="No traces found. Start tracing your msgflux workflows!"
                icon={Activity}
              />
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {recentTraces?.traces.map((trace) => (
                <a
                  key={trace.trace_id}
                  href={`/traces/${trace.trace_id}`}
                  className="block px-6 py-4 hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-medium text-white truncate">
                          {trace.workflow_name || trace.root_span_name || 'Unknown Workflow'}
                        </h4>
                        {trace.error_count > 0 && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-red-500/20 text-red-400">
                            {trace.error_count} error{trace.error_count > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                        <span>{trace.span_count} spans</span>
                        <span>{formatDuration(trace.duration_ms)}</span>
                        <span className="truncate">{trace.trace_id.substring(0, 16)}...</span>
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <div className="text-xs text-gray-400">
                        {new Date(trace.start_time / 1_000_000).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
