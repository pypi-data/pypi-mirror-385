import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-gray-800/50',
        className
      )}
    />
  )
}

export function TraceSkeleton() {
  return (
    <div className="px-6 py-4 border-b border-gray-800">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0 space-y-2">
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-48" />
            <Skeleton className="h-5 w-16" />
          </div>
          <div className="flex items-center gap-4">
            <Skeleton className="h-3 w-64" />
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
    </div>
  )
}

export function TraceListSkeleton() {
  return (
    <div className="divide-y divide-gray-800">
      {[...Array(5)].map((_, i) => (
        <TraceSkeleton key={i} />
      ))}
    </div>
  )
}

export function StatSkeleton() {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-32" />
        </div>
        <Skeleton className="h-12 w-12 rounded-lg" />
      </div>
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900/50">
      <div className="px-6 py-4 border-b border-gray-800">
        <Skeleton className="h-6 w-48" />
      </div>
      <div className="px-6 py-4 space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-5/6" />
      </div>
    </div>
  )
}
