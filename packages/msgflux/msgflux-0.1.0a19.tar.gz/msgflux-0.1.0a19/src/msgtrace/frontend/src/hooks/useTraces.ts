import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchTraces,
  fetchTrace,
  fetchTraceTree,
  deleteTrace,
  fetchStats,
} from '@/lib/api'
import type { TraceQueryParams } from '@/types/trace'

export function useTraces(params: TraceQueryParams = {}) {
  return useQuery({
    queryKey: ['traces', params],
    queryFn: () => fetchTraces(params),
  })
}

export function useTrace(traceId: string) {
  return useQuery({
    queryKey: ['trace', traceId],
    queryFn: () => fetchTrace(traceId),
    enabled: !!traceId,
  })
}

export function useTraceTree(traceId: string) {
  return useQuery({
    queryKey: ['trace-tree', traceId],
    queryFn: () => fetchTraceTree(traceId),
    enabled: !!traceId,
  })
}

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 10000, // Refetch every 10 seconds
  })
}

export function useDeleteTrace() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteTrace,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traces'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}
