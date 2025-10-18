import { useState, useEffect } from 'react'
import type { TraceQueryParams } from '@/types/trace'

const STORAGE_KEY = 'msgtrace_saved_filters'

export interface SavedFilter {
  id: string
  name: string
  query: TraceQueryParams
  createdAt: number
}

export function useSavedFilters() {
  const [savedFilters, setSavedFilters] = useState<SavedFilter[]>([])

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        setSavedFilters(JSON.parse(stored))
      } catch (error) {
        console.error('Failed to parse saved filters:', error)
      }
    }
  }, [])

  // Save to localStorage whenever filters change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(savedFilters))
  }, [savedFilters])

  const saveFilter = (name: string, query: TraceQueryParams) => {
    const filter: SavedFilter = {
      id: `filter_${Date.now()}`,
      name,
      query,
      createdAt: Date.now(),
    }
    setSavedFilters(prev => [...prev, filter])
  }

  const deleteFilter = (id: string) => {
    setSavedFilters(prev => prev.filter(f => f.id !== id))
  }

  const updateFilter = (id: string, name: string, query: TraceQueryParams) => {
    setSavedFilters(prev =>
      prev.map(f => (f.id === id ? { ...f, name, query } : f))
    )
  }

  return {
    savedFilters,
    saveFilter,
    deleteFilter,
    updateFilter,
  }
}
