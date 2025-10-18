import { useState } from 'react'
import { Search, Filter, Trash2, Download, FileJson, FileSpreadsheet } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import AdvancedSearch from '@/components/AdvancedSearch'
import { useTraces, useDeleteTrace } from '@/hooks/useTraces'
import { formatDuration } from '@/types/trace'
import { exportToJSON, exportToCSV, generateFilename } from '@/lib/export'
import { Tooltip } from '@/components/Tooltip'
import type { TraceQueryParams, TraceSummary } from '@/types/trace'

export default function TraceList() {
  const [params, setParams] = useState<TraceQueryParams>({
    limit: 50,
    offset: 0,
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [filteredByAdvanced, setFilteredByAdvanced] = useState<TraceSummary[] | null>(null)

  const { data, isLoading, error } = useTraces(params)
  const deleteMutation = useDeleteTrace()

  const handleDelete = async (traceId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (confirm('Are you sure you want to delete this trace?')) {
      await deleteMutation.mutateAsync(traceId)
    }
  }

  const allTraces = data?.traces || []
  const displayTraces = filteredByAdvanced || allTraces

  const filteredTraces = displayTraces.filter((trace) => {
    if (!searchTerm) return true
    const term = searchTerm.toLowerCase()
    return (
      trace.trace_id.toLowerCase().includes(term) ||
      trace.workflow_name?.toLowerCase().includes(term) ||
      trace.service_name?.toLowerCase().includes(term)
    )
  })

  const handleExportJSON = () => {
    const filename = generateFilename('traces', 'json')
    exportToJSON(filteredTraces, filename)
    setShowExportMenu(false)
  }

  const handleExportCSV = () => {
    const filename = generateFilename('traces', 'csv')
    exportToCSV(filteredTraces, filename)
    setShowExportMenu(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Traces</h1>
          <p className="text-gray-400 mt-2">Browse and search trace data</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              showAdvancedSearch
                ? 'bg-primary-500 text-white'
                : 'bg-gray-800 border border-gray-700 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Advanced Search
          </button>
          <div className="relative">
            <Tooltip content="Export traces">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </Tooltip>
            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10">
                <button
                  onClick={handleExportJSON}
                  className="w-full px-4 py-2 text-left hover:bg-gray-700 transition-colors flex items-center gap-2 text-white"
                >
                  <FileJson className="w-4 h-4" />
                  Export as JSON
                </button>
                <button
                  onClick={handleExportCSV}
                  className="w-full px-4 py-2 text-left hover:bg-gray-700 transition-colors flex items-center gap-2 text-white border-t border-gray-700"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  Export as CSV
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Advanced Search */}
      {showAdvancedSearch && (
        <AdvancedSearch
          traces={allTraces}
          onFilter={(filtered) => setFilteredByAdvanced(filtered)}
          onExport={handleExportJSON}
        />
      )}

      {/* Search and Filters */}
      <Card>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by trace ID, workflow, or service..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-primary-500"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors flex items-center gap-2"
            >
              <Filter className="w-5 h-5" />
              Filters
            </button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-800">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Workflow Name
                </label>
                <input
                  type="text"
                  placeholder="Enter workflow name..."
                  value={params.workflow_name || ''}
                  onChange={(e) => setParams({ ...params, workflow_name: e.target.value || undefined })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Min Duration (ms)
                </label>
                <input
                  type="number"
                  placeholder="0"
                  value={params.min_duration_ms || ''}
                  onChange={(e) => setParams({ ...params, min_duration_ms: e.target.value ? Number(e.target.value) : undefined })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Has Errors
                </label>
                <select
                  value={params.has_errors === undefined ? 'all' : params.has_errors.toString()}
                  onChange={(e) => setParams({ ...params, has_errors: e.target.value === 'all' ? undefined : e.target.value === 'true' })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="all">All</option>
                  <option value="true">With Errors</option>
                  <option value="false">No Errors</option>
                </select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trace List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>
            {filteredTraces?.length || 0} trace{filteredTraces?.length !== 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="px-6 py-12 text-center text-gray-400">Loading...</div>
          ) : error ? (
            <div className="px-6 py-12 text-center text-red-400">
              Error loading traces: {error.message}
            </div>
          ) : filteredTraces?.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-400">
              No traces found
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {filteredTraces?.map((trace) => (
                <a
                  key={trace.trace_id}
                  href={`/traces/${trace.trace_id}`}
                  className="block px-6 py-4 hover:bg-gray-800/50 transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <h4 className="text-sm font-medium text-white truncate">
                          {trace.workflow_name || trace.root_span_name || 'Unknown Workflow'}
                        </h4>
                        {trace.error_count > 0 && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-red-500/20 text-red-400">
                            {trace.error_count} error{trace.error_count > 1 ? 's' : ''}
                          </span>
                        )}
                        {trace.service_name && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-primary-500/20 text-primary-400">
                            {trace.service_name}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span className="font-mono">{trace.trace_id.substring(0, 24)}...</span>
                        <span>{trace.span_count} spans</span>
                        <span>{formatDuration(trace.duration_ms)}</span>
                        <span>{new Date(trace.start_time / 1_000_000).toLocaleString()}</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDelete(trace.trace_id, e)}
                      className="ml-4 p-2 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 rounded-lg transition-all"
                      title="Delete trace"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </a>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {data && data.total > params.limit! && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => setParams({ ...params, offset: Math.max(0, params.offset! - params.limit!) })}
            disabled={params.offset === 0}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-gray-400">
            Showing {params.offset! + 1}-{Math.min(params.offset! + params.limit!, data.total)} of {data.total}
          </span>
          <button
            onClick={() => setParams({ ...params, offset: params.offset! + params.limit! })}
            disabled={params.offset! + params.limit! >= data.total}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
