import { formatDuration, getSpanDurationMs, isSpanError } from '@/types/trace'
import type { Span, Trace } from '@/types/trace'
import { cn } from '@/lib/utils'

interface TimelineProps {
  trace: Trace
  onSpanClick?: (span: Span) => void
}

export default function Timeline({ trace, onSpanClick }: TimelineProps) {
  if (!trace || !trace.spans || trace.spans.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        No spans to display
      </div>
    )
  }

  const traceStart = trace.start_time
  const traceDuration = trace.end_time - trace.start_time

  // Group spans by depth (based on parent-child relationships)
  const spanLevels: Span[][] = []
  const spanDepths = new Map<string, number>()

  function calculateDepth(span: Span): number {
    if (spanDepths.has(span.span_id)) {
      return spanDepths.get(span.span_id)!
    }

    if (!span.parent_span_id) {
      spanDepths.set(span.span_id, 0)
      return 0
    }

    const parent = trace.spans.find(s => s.span_id === span.parent_span_id)
    const depth = parent ? calculateDepth(parent) + 1 : 0
    spanDepths.set(span.span_id, depth)
    return depth
  }

  trace.spans.forEach(span => {
    const depth = calculateDepth(span)
    if (!spanLevels[depth]) {
      spanLevels[depth] = []
    }
    spanLevels[depth].push(span)
  })

  // Calculate position and width percentages
  const getSpanStyle = (span: Span) => {
    const startOffset = span.start_time - traceStart
    const left = (startOffset / traceDuration) * 100
    const width = ((span.end_time - span.start_time) / traceDuration) * 100

    return {
      left: `${left}%`,
      width: `${Math.max(width, 0.5)}%`, // Minimum width for visibility
    }
  }

  const totalDuration = getSpanDurationMs({ start_time: traceStart, end_time: trace.end_time } as Span)

  return (
    <div className="space-y-4">
      {/* Timeline Header */}
      <div className="flex items-center justify-between text-xs text-gray-400 px-4">
        <span>0ms</span>
        <span>Duration: {formatDuration(totalDuration)}</span>
        <span>{formatDuration(totalDuration)}</span>
      </div>

      {/* Timeline Grid */}
      <div className="relative bg-gray-900/50 rounded-lg border border-gray-800 p-4">
        {/* Time markers */}
        <div className="absolute inset-0 flex">
          {[0, 25, 50, 75, 100].map(percent => (
            <div
              key={percent}
              className="flex-none border-l border-gray-800"
              style={{ marginLeft: percent === 0 ? '0' : `${percent}%` }}
            />
          ))}
        </div>

        {/* Spans */}
        <div className="relative space-y-2">
          {spanLevels.map((level, levelIndex) => (
            <div key={levelIndex} className="relative h-8">
              {level.map(span => {
                const duration = getSpanDurationMs(span)
                const isErr = isSpanError(span)

                return (
                  <button
                    key={span.span_id}
                    onClick={() => onSpanClick?.(span)}
                    className={cn(
                      'absolute h-full rounded px-2 flex items-center justify-between overflow-hidden transition-all hover:ring-2 hover:ring-primary-500',
                      isErr
                        ? 'bg-red-500 hover:bg-red-600'
                        : 'bg-primary-600 hover:bg-primary-700'
                    )}
                    style={getSpanStyle(span)}
                    title={`${span.name} - ${formatDuration(duration)}`}
                  >
                    <span className="text-xs text-white truncate font-medium">
                      {span.name}
                    </span>
                    <span className="text-xs text-white/80 ml-2 flex-shrink-0 font-mono">
                      {formatDuration(duration)}
                    </span>
                  </button>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-400 px-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-primary-600" />
          <span>Success</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500" />
          <span>Error</span>
        </div>
      </div>
    </div>
  )
}
