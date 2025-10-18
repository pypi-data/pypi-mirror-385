/**
 * React hooks for Alert management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Alert,
  AlertEvent,
  AlertStats,
  CreateAlertRequest,
  UpdateAlertRequest,
} from '@/types/alert'

// Fetch alerts
export function useAlerts(enabledOnly = false) {
  return useQuery({
    queryKey: ['alerts', enabledOnly],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (enabledOnly) {
        params.append('enabled_only', 'true')
      }

      const response = await api.get(`/api/v1/alerts?${params}`)
      const data = await response.json()
      return {
        alerts: data.alerts as Alert[],
        total: data.total as number,
      }
    },
  })
}

// Fetch single alert
export function useAlert(alertId: string | undefined) {
  return useQuery({
    queryKey: ['alerts', alertId],
    queryFn: async () => {
      if (!alertId) return null
      const response = await api.get(`/api/v1/alerts/${alertId}`)
      return await response.json() as Alert
    },
    enabled: !!alertId,
  })
}

// Create alert
export function useCreateAlert() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (request: CreateAlertRequest) => {
      const response = await api.post('/api/v1/alerts', {
        body: JSON.stringify(request),
        headers: {
          'Content-Type': 'application/json',
        },
      })
      return await response.json() as Alert
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] })
    },
  })
}

// Update alert
export function useUpdateAlert() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ alertId, data }: { alertId: string; data: UpdateAlertRequest }) => {
      const response = await api.patch(`/api/v1/alerts/${alertId}`, {
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json',
        },
      })
      return await response.json() as Alert
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['alerts', variables.alertId] })
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] })
    },
  })
}

// Delete alert
export function useDeleteAlert() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (alertId: string) => {
      await api.delete(`/api/v1/alerts/${alertId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] })
    },
  })
}

// Fetch alert events
export function useAlertEvents(
  alertId?: string,
  limit = 100,
  offset = 0,
  severity?: string,
  acknowledged?: boolean
) {
  return useQuery({
    queryKey: ['alert-events', alertId, limit, offset, severity, acknowledged],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (alertId) params.append('alert_id', alertId)
      params.append('limit', limit.toString())
      params.append('offset', offset.toString())
      if (severity) params.append('severity', severity)
      if (acknowledged !== undefined) params.append('acknowledged', acknowledged.toString())

      const response = await api.get(`/api/v1/alerts/events/list?${params}`)
      const data = await response.json()
      return {
        events: data.events as AlertEvent[],
        total: data.total as number,
        limit: data.limit as number,
        offset: data.offset as number,
      }
    },
  })
}

// Acknowledge alert event
export function useAcknowledgeEvent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ eventId, acknowledgedBy }: { eventId: string; acknowledgedBy: string }) => {
      await api.post(`/api/v1/alerts/events/${eventId}/acknowledge`, {
        body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
        headers: {
          'Content-Type': 'application/json',
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-events'] })
    },
  })
}

// Fetch alert statistics
export function useAlertStats() {
  return useQuery({
    queryKey: ['alert-stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/alerts/stats')
      return await response.json() as AlertStats
    },
  })
}
