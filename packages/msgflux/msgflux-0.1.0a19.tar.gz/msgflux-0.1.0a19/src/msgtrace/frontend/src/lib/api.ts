import type {
  Trace,
  TraceListResponse,
  TraceQueryParams,
  SpanTreeNode,
  Stats,
} from '@/types/trace'

const API_BASE = '/api/v1'

// Generic API client
export const api = {
  get: async (url: string) => {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response
  },
  post: async (url: string, options?: RequestInit) => {
    const response = await fetch(url, { method: 'POST', ...options })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response
  },
  patch: async (url: string, options?: RequestInit) => {
    const response = await fetch(url, { method: 'PATCH', ...options })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response
  },
  delete: async (url: string) => {
    const response = await fetch(url, { method: 'DELETE' })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response
  },
}

export async function fetchTraces(params: TraceQueryParams = {}): Promise<TraceListResponse> {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value))
    }
  })

  const url = `${API_BASE}/traces?${searchParams}`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Failed to fetch traces: ${response.statusText}`)
  }

  return response.json()
}

export async function fetchTrace(traceId: string): Promise<Trace> {
  const response = await fetch(`${API_BASE}/traces/${traceId}`)

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Trace not found')
    }
    throw new Error(`Failed to fetch trace: ${response.statusText}`)
  }

  return response.json()
}

export async function fetchTraceTree(traceId: string): Promise<SpanTreeNode> {
  const response = await fetch(`${API_BASE}/traces/${traceId}/tree`)

  if (!response.ok) {
    throw new Error(`Failed to fetch trace tree: ${response.statusText}`)
  }

  return response.json()
}

export async function deleteTrace(traceId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/traces/${traceId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error(`Failed to delete trace: ${response.statusText}`)
  }
}

export async function fetchStats(): Promise<Stats> {
  const response = await fetch(`${API_BASE}/stats`)

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`)
  }

  return response.json()
}
