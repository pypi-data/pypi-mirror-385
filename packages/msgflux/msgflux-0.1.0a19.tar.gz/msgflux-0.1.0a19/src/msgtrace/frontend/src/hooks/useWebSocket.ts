import { useEffect, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { getWebSocketClient } from '@/lib/websocket'

interface UseWebSocketOptions {
  onTraceCreated?: (traceId: string) => void
  onTraceUpdated?: (traceId: string) => void
  onTraceDeleted?: (traceId: string) => void
  onAlertTriggered?: (alertData: any) => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const queryClient = useQueryClient()

  const connect = useCallback(() => {
    const ws = getWebSocketClient()
    ws.connect()
  }, [])

  const disconnect = useCallback(() => {
    const ws = getWebSocketClient()
    ws.disconnect()
  }, [])

  useEffect(() => {
    const ws = getWebSocketClient()

    // Subscribe to WebSocket messages
    const unsubscribe = ws.subscribe((message) => {
      switch (message.type) {
        case 'connected':
          console.log('✅ WebSocket:', message.data.message)
          break

        case 'trace_created':
          console.log('📊 New trace:', message.data.trace_id)
          // Invalidate traces query to refetch
          queryClient.invalidateQueries({ queryKey: ['traces'] })
          queryClient.invalidateQueries({ queryKey: ['stats'] })
          options.onTraceCreated?.(message.data.trace_id)
          break

        case 'trace_updated':
          console.log('🔄 Trace updated:', message.data.trace_id)
          queryClient.invalidateQueries({ queryKey: ['traces'] })
          queryClient.invalidateQueries({ queryKey: ['trace', message.data.trace_id] })
          options.onTraceUpdated?.(message.data.trace_id)
          break

        case 'trace_deleted':
          console.log('🗑️ Trace deleted:', message.data.trace_id)
          queryClient.invalidateQueries({ queryKey: ['traces'] })
          queryClient.invalidateQueries({ queryKey: ['stats'] })
          // Remove from cache
          queryClient.removeQueries({ queryKey: ['trace', message.data.trace_id] })
          options.onTraceDeleted?.(message.data.trace_id)
          break

        case 'stats_updated':
          console.log('📈 Stats updated')
          queryClient.invalidateQueries({ queryKey: ['stats'] })
          break

        case 'alert_triggered':
          console.log('🚨 Alert triggered:', message.data.alert_name)
          // Invalidate alert-related queries
          queryClient.invalidateQueries({ queryKey: ['alert-events'] })
          queryClient.invalidateQueries({ queryKey: ['alert-stats'] })
          queryClient.invalidateQueries({ queryKey: ['alerts'] })
          options.onAlertTriggered?.(message.data)
          break
      }
    })

    // Connect on mount
    ws.connect()

    // Cleanup on unmount
    return () => {
      unsubscribe()
      ws.disconnect()
    }
  }, [queryClient, options])

  return { connect, disconnect }
}
