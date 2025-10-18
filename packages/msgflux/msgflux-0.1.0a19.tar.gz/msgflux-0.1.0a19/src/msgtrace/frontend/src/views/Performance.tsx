import { useState } from 'react'
import { Activity, Clock, TrendingUp, AlertTriangle, BarChart3, Filter } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import {
  useLatencyPercentiles,
  useLatencyTimeSeries,
  useErrorTimeSeries,
  useThroughputTimeSeries,
  useWorkflowComparison,
  useAvailableWorkflows,
} from '@/hooks/useAnalytics'
import { formatLatency } from '@/types/analytics'

export default function Performance() {
  const [timeWindow, setTimeWindow] = useState(24)
  const [bucketSize, setBucketSize] = useState(60)
  const [showFilters, setShowFilters] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | undefined>(undefined)

  const { workflows } = useAvailableWorkflows(timeWindow)

  const { data: percentiles } = useLatencyPercentiles(timeWindow, selectedWorkflow)
  const { data: latencyData, isLoading: loadingLatency } = useLatencyTimeSeries(
    timeWindow,
    bucketSize,
    selectedWorkflow
  )
  const { data: errorData, isLoading: loadingErrors } = useErrorTimeSeries(
    timeWindow,
    bucketSize,
    selectedWorkflow
  )
  const { data: throughputData, isLoading: loadingThroughput } = useThroughputTimeSeries(
    timeWindow,
    bucketSize,
    selectedWorkflow
  )
  const { data: workflowData, isLoading: loadingWorkflows } = useWorkflowComparison(timeWindow)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Performance Monitoring</h1>
          <p className="text-gray-400 mt-2">Advanced metrics and analytics</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <Filter className="w-4 h-4" />
          Settings
        </button>
      </div>

      {/* Settings Panel */}
      {showFilters && (
        <Card>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Time Window
                </label>
                <select
                  value={timeWindow}
                  onChange={(e) => setTimeWindow(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value={1}>Last 1 hour</option>
                  <option value={6}>Last 6 hours</option>
                  <option value={24}>Last 24 hours</option>
                  <option value={72}>Last 3 days</option>
                  <option value={168}>Last 7 days</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Bucket Size
                </label>
                <select
                  value={bucketSize}
                  onChange={(e) => setBucketSize(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value={5}>5 minutes</option>
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                  <option value={360}>6 hours</option>
                  <option value={1440}>1 day</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Workflow Filter
                </label>
                <select
                  value={selectedWorkflow ?? ''}
                  onChange={(e) => setSelectedWorkflow(e.target.value || undefined)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="">All Workflows</option>
                  {workflows.map((workflow) => (
                    <option key={workflow} value={workflow}>
                      {workflow}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Percentile Stats Cards */}
      {percentiles && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">P50 (Median)</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {formatLatency(percentiles.p50)}
                </p>
                <p className="text-xs text-gray-500 mt-1">{percentiles.count} traces</p>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10">
                <Clock className="w-6 h-6 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">P95</p>
                <p className="text-2xl font-bold text-yellow-400 mt-1">
                  {formatLatency(percentiles.p95)}
                </p>
                <p className="text-xs text-gray-500 mt-1">95th percentile</p>
              </div>
              <div className="p-3 rounded-lg bg-yellow-500/10">
                <TrendingUp className="w-6 h-6 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">P99</p>
                <p className="text-2xl font-bold text-red-400 mt-1">
                  {formatLatency(percentiles.p99)}
                </p>
                <p className="text-xs text-gray-500 mt-1">99th percentile</p>
              </div>
              <div className="p-3 rounded-lg bg-red-500/10">
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Mean</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {formatLatency(percentiles.mean)}
                </p>
                <p className="text-xs text-gray-500 mt-1">Average latency</p>
              </div>
              <div className="p-3 rounded-lg bg-primary-500/10">
                <Activity className="w-6 h-6 text-primary-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Latency Over Time Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Latency Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingLatency ? (
            <div className="h-80 flex items-center justify-center text-gray-400">
              Loading...
            </div>
          ) : latencyData && latencyData.buckets.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={latencyData.buckets}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="time"
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF' }} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#F3F4F6' }}
                  itemStyle={{ color: '#F3F4F6' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="p50"
                  stroke="#3B82F6"
                  name="P50"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="p95"
                  stroke="#F59E0B"
                  name="P95"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="mean"
                  stroke="#10B981"
                  name="Mean"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Rate Over Time Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Error Rate Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingErrors ? (
            <div className="h-80 flex items-center justify-center text-gray-400">
              Loading...
            </div>
          ) : errorData && errorData.buckets.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={errorData.buckets}>
                <defs>
                  <linearGradient id="colorError" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="time"
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF' }} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#F3F4F6' }}
                  itemStyle={{ color: '#F3F4F6' }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="error_rate"
                  stroke="#EF4444"
                  fillOpacity={1}
                  fill="url(#colorError)"
                  name="Error Rate (%)"
                />
                <Area
                  type="monotone"
                  dataKey="success_rate"
                  stroke="#10B981"
                  fillOpacity={1}
                  fill="url(#colorSuccess)"
                  name="Success Rate (%)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Throughput Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Trace Throughput</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingThroughput ? (
            <div className="h-80 flex items-center justify-center text-gray-400">
              Loading...
            </div>
          ) : throughputData && throughputData.buckets.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={throughputData.buckets}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="time"
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF' }} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#F3F4F6' }}
                  itemStyle={{ color: '#F3F4F6' }}
                />
                <Legend />
                <Bar dataKey="count" fill="#8B5CF6" name="Trace Count" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Workflow Comparison Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Workflow Performance Comparison
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loadingWorkflows ? (
            <div className="px-6 py-12 text-center text-gray-400">Loading...</div>
          ) : workflowData && workflowData.workflows.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800 border-b border-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Workflow
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Count
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      P50
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      P95
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Mean
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Error Rate
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {workflowData.workflows.map((workflow) => (
                    <tr key={workflow.workflow_name} className="hover:bg-gray-800/50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-mono">
                        {workflow.workflow_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 text-right">
                        {workflow.count.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-400 text-right">
                        {formatLatency(workflow.p50)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-400 text-right">
                        {formatLatency(workflow.p95)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400 text-right">
                        {formatLatency(workflow.mean)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            workflow.error_rate > 10
                              ? 'bg-red-500/20 text-red-400'
                              : workflow.error_rate > 5
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-green-500/20 text-green-400'
                          }`}
                        >
                          {workflow.error_rate.toFixed(2)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="px-6 py-12 text-center text-gray-400">
              No workflow data available
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
