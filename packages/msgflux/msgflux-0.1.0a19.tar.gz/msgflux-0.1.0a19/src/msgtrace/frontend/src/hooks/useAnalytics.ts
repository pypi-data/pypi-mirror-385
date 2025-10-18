/**
 * React hooks for Analytics data
 */

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  LatencyPercentiles,
  LatencyTimeSeries,
  ErrorTimeSeries,
  ThroughputTimeSeries,
  WorkflowComparison,
} from '@/types/analytics'

// Fetch latency percentiles
export function useLatencyPercentiles(
  hours = 24,
  workflowName?: string,
  serviceName?: string
) {
  return useQuery({
    queryKey: ['analytics', 'latency-percentiles', hours, workflowName, serviceName],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('hours', hours.toString())
      if (workflowName) params.append('workflow_name', workflowName)
      if (serviceName) params.append('service_name', serviceName)

      const response = await api.get(`/api/v1/analytics/latency-percentiles?${params}`)
      return await response.json() as LatencyPercentiles
    },
    refetchInterval: 60000, // Refetch every minute
  })
}

// Fetch latency time series
export function useLatencyTimeSeries(
  hours = 24,
  bucketMinutes = 60,
  workflowName?: string
) {
  return useQuery({
    queryKey: ['analytics', 'timeseries-latency', hours, bucketMinutes, workflowName],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('hours', hours.toString())
      params.append('bucket_minutes', bucketMinutes.toString())
      if (workflowName) params.append('workflow_name', workflowName)

      const response = await api.get(`/api/v1/analytics/timeseries/latency?${params}`)
      return await response.json() as LatencyTimeSeries
    },
    refetchInterval: 60000,
  })
}

// Fetch error time series
export function useErrorTimeSeries(
  hours = 24,
  bucketMinutes = 60,
  workflowName?: string
) {
  return useQuery({
    queryKey: ['analytics', 'timeseries-errors', hours, bucketMinutes, workflowName],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('hours', hours.toString())
      params.append('bucket_minutes', bucketMinutes.toString())
      if (workflowName) params.append('workflow_name', workflowName)

      const response = await api.get(`/api/v1/analytics/timeseries/errors?${params}`)
      return await response.json() as ErrorTimeSeries
    },
    refetchInterval: 60000,
  })
}

// Fetch throughput time series
export function useThroughputTimeSeries(
  hours = 24,
  bucketMinutes = 60,
  workflowName?: string
) {
  return useQuery({
    queryKey: ['analytics', 'timeseries-throughput', hours, bucketMinutes, workflowName],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('hours', hours.toString())
      params.append('bucket_minutes', bucketMinutes.toString())
      if (workflowName) params.append('workflow_name', workflowName)

      const response = await api.get(`/api/v1/analytics/timeseries/throughput?${params}`)
      return await response.json() as ThroughputTimeSeries
    },
    refetchInterval: 60000,
  })
}

// Fetch workflow comparison
export function useWorkflowComparison(hours = 24) {
  return useQuery({
    queryKey: ['analytics', 'workflow-comparison', hours],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('hours', hours.toString())

      const response = await api.get(`/api/v1/analytics/workflow-comparison?${params}`)
      return await response.json() as WorkflowComparison
    },
    refetchInterval: 60000,
  })
}

// Fetch available workflow names
export function useAvailableWorkflows(hours = 24) {
  const { data: workflowData } = useWorkflowComparison(hours)

  return {
    workflows: workflowData?.workflows.map(w => w.workflow_name) ?? [],
    isLoading: !workflowData,
  }
}
