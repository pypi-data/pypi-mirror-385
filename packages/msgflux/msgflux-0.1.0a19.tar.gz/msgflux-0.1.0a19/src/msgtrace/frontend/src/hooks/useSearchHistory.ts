import { useState, useEffect } from 'react'

const STORAGE_KEY = 'msgtrace_search_history'
const MAX_HISTORY = 20

export function useSearchHistory() {
  const [history, setHistory] = useState<string[]>([])

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        setHistory(JSON.parse(stored))
      } catch (error) {
        console.error('Failed to parse search history:', error)
      }
    }
  }, [])

  // Save to localStorage whenever history changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
  }, [history])

  const addToHistory = (query: string) => {
    if (!query.trim()) return

    setHistory(prev => {
      // Remove duplicates and add to front
      const filtered = prev.filter(q => q !== query)
      const updated = [query, ...filtered]

      // Keep only MAX_HISTORY items
      return updated.slice(0, MAX_HISTORY)
    })
  }

  const removeFromHistory = (query: string) => {
    setHistory(prev => prev.filter(q => q !== query))
  }

  const clearHistory = () => {
    setHistory([])
  }

  return {
    history,
    addToHistory,
    removeFromHistory,
    clearHistory,
  }
}
