/**
 * Alert Types for msgtrace Frontend
 */

export type AlertConditionType =
  | 'duration_threshold'
  | 'error_rate'
  | 'cost_threshold'
  | 'span_count'
  | 'error_count'

export type AlertOperator = 'gt' | 'lt' | 'gte' | 'lte' | 'eq' | 'neq'

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical'

export type NotificationChannel = 'webhook' | 'email' | 'slack' | 'console'

export interface AlertCondition {
  condition_type: AlertConditionType
  operator: AlertOperator
  threshold: number
  field?: string
}

export interface NotificationConfig {
  channel: NotificationChannel
  config: Record<string, unknown>
  enabled: boolean
}

export interface Alert {
  id: string
  name: string
  description?: string
  condition: AlertCondition
  severity: AlertSeverity
  notifications: NotificationConfig[]
  enabled: boolean
  cooldown_minutes: number
  workflow_filter?: string
  service_filter?: string
  created_at: number
  updated_at: number
  last_triggered_at?: number
  trigger_count: number
}

export interface AlertEvent {
  id: string
  alert_id: string
  alert_name: string
  severity: AlertSeverity
  trace_id: string
  workflow_name?: string
  service_name?: string
  condition_type: AlertConditionType
  threshold: number
  actual_value: number
  message: string
  triggered_at: number
  acknowledged: boolean
  acknowledged_at?: number
  acknowledged_by?: string
}

export interface AlertStats {
  total_alerts: number
  enabled_alerts: number
  total_events: number
  events_last_24h: number
  events_by_severity: Record<string, number>
  most_triggered_alert?: {
    name: string
    count: number
  }
}

export interface CreateAlertRequest {
  name: string
  description?: string
  condition: AlertCondition
  severity: AlertSeverity
  notifications: NotificationConfig[]
  enabled?: boolean
  cooldown_minutes?: number
  workflow_filter?: string
  service_filter?: string
}

export interface UpdateAlertRequest {
  name?: string
  description?: string
  condition?: AlertCondition
  severity?: AlertSeverity
  notifications?: NotificationConfig[]
  enabled?: boolean
  cooldown_minutes?: number
  workflow_filter?: string
  service_filter?: string
}

// Helper functions
export function formatConditionType(type: AlertConditionType): string {
  const map: Record<AlertConditionType, string> = {
    duration_threshold: 'Duration',
    error_rate: 'Error Rate',
    cost_threshold: 'Cost',
    span_count: 'Span Count',
    error_count: 'Error Count',
  }
  return map[type] || type
}

export function formatOperator(operator: AlertOperator): string {
  const map: Record<AlertOperator, string> = {
    gt: '>',
    lt: '<',
    gte: '>=',
    lte: '<=',
    eq: '=',
    neq: '!=',
  }
  return map[operator] || operator
}

export function formatSeverity(severity: AlertSeverity): string {
  return severity.charAt(0).toUpperCase() + severity.slice(1)
}

export function getSeverityColor(severity: AlertSeverity): string {
  const colors = {
    info: 'text-blue-400 bg-blue-500/20',
    warning: 'text-yellow-400 bg-yellow-500/20',
    error: 'text-red-400 bg-red-500/20',
    critical: 'text-purple-400 bg-purple-500/20',
  }
  return colors[severity] || colors.info
}

export function formatThreshold(conditionType: AlertConditionType, threshold: number): string {
  switch (conditionType) {
    case 'duration_threshold':
      return `${threshold}ms`
    case 'error_rate':
      return `${threshold}%`
    case 'cost_threshold':
      return `$${threshold.toFixed(6)}`
    case 'span_count':
    case 'error_count':
      return threshold.toString()
    default:
      return threshold.toString()
  }
}

export function formatValue(conditionType: AlertConditionType, value: number): string {
  return formatThreshold(conditionType, value)
}
