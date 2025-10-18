import { useState } from 'react'
import { Plus, Bell, BellOff, Trash2, Edit, Activity } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import { useAlerts, useDeleteAlert, useUpdateAlert, useAlertStats } from '@/hooks/useAlerts'
import { Alert as AlertType } from '@/types/alert'
import {
  formatConditionType,
  formatOperator,
  formatSeverity,
  getSeverityColor,
  formatThreshold,
} from '@/types/alert'
import { Tooltip } from '@/components/Tooltip'

export default function Alerts() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const { data: alertsData, isLoading, error } = useAlerts()
  const { data: stats } = useAlertStats()
  const deleteMutation = useDeleteAlert()
  const updateMutation = useUpdateAlert()

  const handleDelete = async (alertId: string) => {
    if (confirm('Are you sure you want to delete this alert?')) {
      await deleteMutation.mutateAsync(alertId)
    }
  }

  const handleToggle = async (alert: AlertType) => {
    await updateMutation.mutateAsync({
      alertId: alert.id,
      data: { enabled: !alert.enabled },
    })
  }

  const alerts = alertsData?.alerts || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Alerts</h1>
          <p className="text-gray-400 mt-2">Configure and manage alert rules</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg text-white transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create Alert
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Total Alerts</p>
                <p className="text-2xl font-bold text-white mt-1">{stats.total_alerts}</p>
              </div>
              <div className="p-3 rounded-lg bg-primary-500/10">
                <Bell className="w-6 h-6 text-primary-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Enabled</p>
                <p className="text-2xl font-bold text-green-400 mt-1">{stats.enabled_alerts}</p>
              </div>
              <div className="p-3 rounded-lg bg-green-500/10">
                <Bell className="w-6 h-6 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Events (24h)</p>
                <p className="text-2xl font-bold text-yellow-400 mt-1">{stats.events_last_24h}</p>
              </div>
              <div className="p-3 rounded-lg bg-yellow-500/10">
                <Activity className="w-6 h-6 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Total Events</p>
                <p className="text-2xl font-bold text-white mt-1">{stats.total_events}</p>
              </div>
              <div className="p-3 rounded-lg bg-gray-500/10">
                <Activity className="w-6 h-6 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alerts List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Alert Rules ({alerts.length})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="px-6 py-12 text-center text-gray-400">Loading...</div>
          ) : error ? (
            <div className="px-6 py-12 text-center text-red-400">
              Error loading alerts: {error.message}
            </div>
          ) : alerts.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <Bell className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">No alerts configured yet</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg text-white transition-colors"
              >
                Create Your First Alert
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="px-6 py-4 hover:bg-gray-800/50 transition-colors group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-base font-medium text-white">{alert.name}</h4>
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded ${getSeverityColor(
                            alert.severity
                          )}`}
                        >
                          {formatSeverity(alert.severity)}
                        </span>
                        {!alert.enabled && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-gray-700 text-gray-400">
                            Disabled
                          </span>
                        )}
                      </div>

                      {alert.description && (
                        <p className="text-sm text-gray-400 mb-2">{alert.description}</p>
                      )}

                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span>
                          {formatConditionType(alert.condition.condition_type)}{' '}
                          {formatOperator(alert.condition.operator)}{' '}
                          {formatThreshold(alert.condition.condition_type, alert.condition.threshold)}
                        </span>
                        {alert.workflow_filter && (
                          <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                            workflow: {alert.workflow_filter}
                          </span>
                        )}
                        {alert.service_filter && (
                          <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                            service: {alert.service_filter}
                          </span>
                        )}
                        <span>Cooldown: {alert.cooldown_minutes}m</span>
                        <span>Triggers: {alert.trigger_count}</span>
                        {alert.notifications.length > 0 && (
                          <span>
                            {alert.notifications.length} notification
                            {alert.notifications.length > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Tooltip content={alert.enabled ? 'Disable' : 'Enable'}>
                        <button
                          onClick={() => handleToggle(alert)}
                          className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                        >
                          {alert.enabled ? (
                            <Bell className="w-4 h-4 text-green-400" />
                          ) : (
                            <BellOff className="w-4 h-4 text-gray-400" />
                          )}
                        </button>
                      </Tooltip>
                      <Tooltip content="Edit">
                        <button
                          onClick={() => {
                            // TODO: Implement edit
                            window.alert('Edit not yet implemented')
                          }}
                          className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4 text-gray-400" />
                        </button>
                      </Tooltip>
                      <Tooltip content="Delete">
                        <button
                          onClick={() => handleDelete(alert.id)}
                          className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </Tooltip>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-4">Create Alert (Coming Soon)</h2>
            <p className="text-gray-400 mb-6">
              Alert creation UI will be available in the next iteration.
            </p>
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
