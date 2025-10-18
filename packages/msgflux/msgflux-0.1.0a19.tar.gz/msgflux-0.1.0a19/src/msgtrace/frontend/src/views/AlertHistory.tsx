import { useState } from 'react'
import { Check, AlertCircle, Filter } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import { useAlertEvents, useAcknowledgeEvent } from '@/hooks/useAlerts'
import { AlertEvent } from '@/types/alert'
import { getSeverityColor, formatSeverity, formatValue } from '@/types/alert'

export default function AlertHistory() {
  const [severity, setSeverity] = useState<string | undefined>(undefined)
  const [acknowledgedFilter, setAcknowledgedFilter] = useState<boolean | undefined>(undefined)
  const [showFilters, setShowFilters] = useState(false)

  const { data, isLoading, error } = useAlertEvents(
    undefined,
    100,
    0,
    severity,
    acknowledgedFilter
  )
  const acknowledgeMutation = useAcknowledgeEvent()

  const handleAcknowledge = async (event: AlertEvent) => {
    await acknowledgeMutation.mutateAsync({
      eventId: event.id,
      acknowledgedBy: 'user', // TODO: Get actual user
    })
  }

  const events = data?.events || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Alert History</h1>
          <p className="text-gray-400 mt-2">View all triggered alerts</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Severity</label>
                <select
                  value={severity || 'all'}
                  onChange={(e) => setSeverity(e.target.value === 'all' ? undefined : e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="all">All Severities</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Status</label>
                <select
                  value={
                    acknowledgedFilter === undefined
                      ? 'all'
                      : acknowledgedFilter
                      ? 'acknowledged'
                      : 'unacknowledged'
                  }
                  onChange={(e) =>
                    setAcknowledgedFilter(
                      e.target.value === 'all'
                        ? undefined
                        : e.target.value === 'acknowledged'
                    )
                  }
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="all">All</option>
                  <option value="unacknowledged">Unacknowledged</option>
                  <option value="acknowledged">Acknowledged</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Events List */}
      <Card>
        <CardHeader>
          <CardTitle>{events.length} events</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="px-6 py-12 text-center text-gray-400">Loading...</div>
          ) : error ? (
            <div className="px-6 py-12 text-center text-red-400">
              Error loading events: {error.message}
            </div>
          ) : events.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-400">
              No alert events found
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {events.map((event) => (
                <div
                  key={event.id}
                  className={`px-6 py-4 hover:bg-gray-800/50 transition-colors group ${
                    event.acknowledged ? 'opacity-60' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <AlertCircle
                          className={`w-5 h-5 flex-shrink-0 ${
                            event.severity === 'critical'
                              ? 'text-purple-400'
                              : event.severity === 'error'
                              ? 'text-red-400'
                              : event.severity === 'warning'
                              ? 'text-yellow-400'
                              : 'text-blue-400'
                          }`}
                        />
                        <h4 className="text-base font-medium text-white">{event.alert_name}</h4>
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded ${getSeverityColor(
                            event.severity
                          )}`}
                        >
                          {formatSeverity(event.severity)}
                        </span>
                        {event.acknowledged && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-green-500/20 text-green-400 flex items-center gap-1">
                            <Check className="w-3 h-3" />
                            Acknowledged
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-gray-300 mb-2">{event.message}</p>

                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span className="font-mono">{event.trace_id.substring(0, 16)}...</span>
                        {event.workflow_name && (
                          <span>Workflow: {event.workflow_name}</span>
                        )}
                        {event.service_name && <span>Service: {event.service_name}</span>}
                        <span>
                          Threshold: {formatValue(event.condition_type, event.threshold)}
                        </span>
                        <span>
                          Actual: {formatValue(event.condition_type, event.actual_value)}
                        </span>
                        <span>{new Date(event.triggered_at).toLocaleString()}</span>
                      </div>

                      {event.acknowledged && event.acknowledged_by && (
                        <div className="text-xs text-gray-500 mt-1">
                          Acknowledged by {event.acknowledged_by}{' '}
                          {event.acknowledged_at &&
                            `at ${new Date(event.acknowledged_at).toLocaleString()}`}
                        </div>
                      )}
                    </div>

                    {!event.acknowledged && (
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleAcknowledge(event)}
                          className="px-3 py-1.5 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-green-400 text-sm transition-colors flex items-center gap-1"
                        >
                          <Check className="w-4 h-4" />
                          Acknowledge
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
