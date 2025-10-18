import { ChevronDown, ChevronRight, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'
import { formatDuration, getSpanDurationMs, isSpanError } from '@/types/trace'
import type { SpanTreeNode, Span } from '@/types/trace'
import { cn } from '@/lib/utils'

interface SpanTreeProps {
  tree: SpanTreeNode
  onSpanClick?: (span: Span) => void
}

interface TreeNodeProps {
  node: SpanTreeNode
  depth: number
  onSpanClick?: (span: Span) => void
}

function TreeNode({ node, depth, onSpanClick }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(depth < 2) // Auto-expand first 2 levels
  const { span, children } = node
  const hasChildren = children && children.length > 0
  const isError = isSpanError(span)
  const duration = getSpanDurationMs(span)

  return (
    <div className="text-sm">
      <button
        onClick={() => {
          if (hasChildren) {
            setIsExpanded(!isExpanded)
          }
          onSpanClick?.(span)
        }}
        className={cn(
          'w-full px-3 py-2 flex items-center gap-2 hover:bg-gray-800/50 rounded transition-colors text-left',
          isError && 'bg-red-500/5'
        )}
        style={{ paddingLeft: `${depth * 1.5 + 0.75}rem` }}
      >
        {/* Expand/Collapse Icon */}
        <div className="w-4 h-4 flex-shrink-0">
          {hasChildren && (
            isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )
          )}
        </div>

        {/* Status Icon */}
        {isError ? (
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
        ) : (
          <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
        )}

        {/* Span Name */}
        <span className={cn('flex-1 min-w-0 truncate', isError ? 'text-red-300' : 'text-gray-200')}>
          {span.name}
        </span>

        {/* Duration */}
        <span className="text-xs text-gray-400 flex-shrink-0 font-mono">
          {formatDuration(duration)}
        </span>

        {/* Span Kind Badge */}
        <span className="px-2 py-0.5 text-xs rounded bg-primary-500/20 text-primary-400 flex-shrink-0">
          {span.kind}
        </span>
      </button>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="mt-0.5">
          {children.map((child) => (
            <TreeNode
              key={child.span.span_id}
              node={child}
              depth={depth + 1}
              onSpanClick={onSpanClick}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function SpanTree({ tree, onSpanClick }: SpanTreeProps) {
  if (!tree || !tree.span) {
    return (
      <div className="text-center py-8 text-gray-400">
        No span tree available
      </div>
    )
  }

  return (
    <div className="space-y-1">
      <TreeNode node={tree} depth={0} onSpanClick={onSpanClick} />
    </div>
  )
}
