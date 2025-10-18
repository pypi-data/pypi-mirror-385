import { useState } from 'react'
import { Search, X, History, Bookmark, HelpCircle, Download } from 'lucide-react'
import { parseQuery, applyFilters } from '@/lib/queryParser'
import { useSearchHistory } from '@/hooks/useSearchHistory'
import { useSavedFilters } from '@/hooks/useSavedFilters'
import { Tooltip } from './Tooltip'
import type { TraceSummary } from '@/types/trace'

interface AdvancedSearchProps {
  traces: TraceSummary[]
  onFilter: (filtered: TraceSummary[]) => void
  onExport?: () => void
}

export default function AdvancedSearch({ traces, onFilter, onExport }: AdvancedSearchProps) {
  const [query, setQuery] = useState('')
  const [showHelp, setShowHelp] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [showSaved, setShowSaved] = useState(false)
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [filterName, setFilterName] = useState('')

  const { history, addToHistory, removeFromHistory, clearHistory } = useSearchHistory()
  const { savedFilters, saveFilter, deleteFilter } = useSavedFilters()

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery)

    if (!searchQuery.trim()) {
      onFilter(traces)
      return
    }

    const parsed = parseQuery(searchQuery)

    if (parsed.error) {
      console.error('Query parse error:', parsed.error)
      return
    }

    const filtered = applyFilters(traces, parsed.filters)
    onFilter(filtered)
    addToHistory(searchQuery)
    setShowHistory(false)
  }

  const handleSaveFilter = () => {
    if (filterName.trim() && query.trim()) {
      const parsed = parseQuery(query)
      if (!parsed.error && parsed.filters.length > 0) {
        // Convert filters back to TraceQueryParams
        const queryParams: any = {}
        parsed.filters.forEach(filter => {
          if (filter.field === 'duration_ms' && filter.operator === 'gt') {
            queryParams.min_duration_ms = Number(filter.value)
          } else if (filter.field === 'duration_ms' && filter.operator === 'lt') {
            queryParams.max_duration_ms = Number(filter.value)
          } else if (filter.field === 'has_errors') {
            queryParams.has_errors = Boolean(filter.value)
          } else if (filter.field === 'workflow_name') {
            queryParams.workflow_name = String(filter.value)
          } else if (filter.field === 'service_name') {
            queryParams.service_name = String(filter.value)
          }
        })

        saveFilter(filterName, queryParams)
        setFilterName('')
        setSaveDialogOpen(false)
      }
    }
  }

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Advanced search: duration:>1000ms AND error:true"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch(query)
              }
            }}
            className="w-full pl-10 pr-20 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-primary-500"
          />
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex gap-1">
            {query && (
              <button
                onClick={() => {
                  setQuery('')
                  onFilter(traces)
                }}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                title="Clear"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            )}
            <Tooltip content="Search syntax help">
              <button
                onClick={() => setShowHelp(!showHelp)}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors"
              >
                <HelpCircle className="w-4 h-4 text-gray-400" />
              </button>
            </Tooltip>
          </div>
        </div>

        <button
          onClick={() => handleSearch(query)}
          className="px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg text-white transition-colors"
        >
          Search
        </button>

        <Tooltip content="Search history">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors"
          >
            <History className="w-5 h-5" />
          </button>
        </Tooltip>

        <Tooltip content="Saved filters">
          <button
            onClick={() => setShowSaved(!showSaved)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors"
          >
            <Bookmark className="w-5 h-5" />
          </button>
        </Tooltip>

        {onExport && (
          <Tooltip content="Export results">
            <button
              onClick={onExport}
              className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition-colors"
            >
              <Download className="w-5 h-5" />
            </button>
          </Tooltip>
        )}
      </div>

      {/* Help Panel */}
      {showHelp && (
        <div className="p-4 bg-gray-800 border border-gray-700 rounded-lg text-sm space-y-3">
          <h4 className="font-semibold text-white">Search Syntax:</h4>
          <div className="grid grid-cols-2 gap-2 text-gray-300">
            <code>duration:&gt;1000ms</code>
            <span className="text-gray-400">Duration greater than 1s</span>

            <code>duration:&lt;500ms</code>
            <span className="text-gray-400">Duration less than 500ms</span>

            <code>error:true</code>
            <span className="text-gray-400">Has errors</span>

            <code>spans:&gt;10</code>
            <span className="text-gray-400">More than 10 spans</span>

            <code>workflow:agent*</code>
            <span className="text-gray-400">Workflow starts with "agent"</span>

            <code>service:*api</code>
            <span className="text-gray-400">Service ends with "api"</span>
          </div>
          <div className="pt-2 border-t border-gray-700">
            <p className="text-gray-400">
              Combine with <code className="text-primary-400">AND</code> or <code className="text-primary-400">OR</code>:
            </p>
            <code className="text-gray-300">duration:&gt;1000ms AND error:true</code>
          </div>
        </div>
      )}

      {/* Search History */}
      {showHistory && history.length > 0 && (
        <div className="p-4 bg-gray-800 border border-gray-700 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-white text-sm">Recent Searches</h4>
            <button
              onClick={clearHistory}
              className="text-xs text-gray-400 hover:text-white transition-colors"
            >
              Clear All
            </button>
          </div>
          <div className="space-y-1">
            {history.map((item, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 hover:bg-gray-700 rounded transition-colors group"
              >
                <button
                  onClick={() => {
                    setQuery(item)
                    handleSearch(item)
                  }}
                  className="flex-1 text-left text-sm text-gray-300 font-mono"
                >
                  {item}
                </button>
                <button
                  onClick={() => removeFromHistory(item)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-600 rounded transition-all"
                >
                  <X className="w-3 h-3 text-gray-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Saved Filters */}
      {showSaved && (
        <div className="p-4 bg-gray-800 border border-gray-700 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-white text-sm">Saved Filters</h4>
            {query && (
              <button
                onClick={() => setSaveDialogOpen(!saveDialogOpen)}
                className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
              >
                + Save Current
              </button>
            )}
          </div>

          {saveDialogOpen && (
            <div className="mb-3 p-3 bg-gray-900 rounded border border-gray-700">
              <input
                type="text"
                placeholder="Filter name..."
                value={filterName}
                onChange={(e) => setFilterName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSaveFilter()
                  }
                }}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-400 focus:outline-none focus:border-primary-500 mb-2"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSaveFilter}
                  className="px-3 py-1 bg-primary-500 hover:bg-primary-600 rounded text-white text-sm transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setSaveDialogOpen(false)
                    setFilterName('')
                  }}
                  className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-white text-sm transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {savedFilters.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">
              No saved filters yet
            </p>
          ) : (
            <div className="space-y-1">
              {savedFilters.map((filter) => (
                <div
                  key={filter.id}
                  className="flex items-center justify-between p-2 hover:bg-gray-700 rounded transition-colors group"
                >
                  <button
                    onClick={() => {
                      // Build query from saved params
                      const parts: string[] = []
                      if (filter.query.min_duration_ms) {
                        parts.push(`duration:>${filter.query.min_duration_ms}ms`)
                      }
                      if (filter.query.max_duration_ms) {
                        parts.push(`duration:<${filter.query.max_duration_ms}ms`)
                      }
                      if (filter.query.has_errors !== undefined) {
                        parts.push(`error:${filter.query.has_errors}`)
                      }
                      if (filter.query.workflow_name) {
                        parts.push(`workflow:${filter.query.workflow_name}`)
                      }
                      const queryStr = parts.join(' AND ')
                      setQuery(queryStr)
                      handleSearch(queryStr)
                    }}
                    className="flex-1 text-left"
                  >
                    <div className="text-sm text-white font-medium">{filter.name}</div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      {new Date(filter.createdAt).toLocaleDateString()}
                    </div>
                  </button>
                  <button
                    onClick={() => deleteFilter(filter.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-600 rounded transition-all"
                  >
                    <X className="w-3 h-3 text-gray-400" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
