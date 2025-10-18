/**
 * Query Parser for Advanced Search
 *
 * Supports queries like:
 * - duration:>1000ms
 * - error:true
 * - workflow:agent*
 * - spans:>10
 * - duration:>500ms AND error:true
 * - workflow:sentiment* OR workflow:agent*
 */

export interface ParsedQuery {
  filters: QueryFilter[]
  error?: string
}

export interface QueryFilter {
  field: string
  operator: 'eq' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains' | 'startswith' | 'endswith'
  value: string | number | boolean
  combinator?: 'AND' | 'OR'
}

const FIELD_MAPPINGS: Record<string, string> = {
  'duration': 'duration_ms',
  'spans': 'span_count',
  'errors': 'error_count',
  'error': 'has_errors',
  'workflow': 'workflow_name',
  'service': 'service_name',
  'time': 'start_time',
}

const TIME_UNITS: Record<string, number> = {
  'ms': 1,
  's': 1000,
  'm': 60000,
  'h': 3600000,
}

export function parseQuery(query: string): ParsedQuery {
  if (!query.trim()) {
    return { filters: [] }
  }

  try {
    const filters: QueryFilter[] = []

    // Split by AND/OR (case insensitive)
    const parts = query.split(/\s+(AND|OR)\s+/i)

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i].trim()

      // Skip combinators
      if (part.toUpperCase() === 'AND' || part.toUpperCase() === 'OR') {
        continue
      }

      // Parse individual filter
      const filter = parseFilter(part)
      if (filter) {
        // Add combinator from previous part
        if (i > 0 && (parts[i - 1].toUpperCase() === 'AND' || parts[i - 1].toUpperCase() === 'OR')) {
          filter.combinator = parts[i - 1].toUpperCase() as 'AND' | 'OR'
        }
        filters.push(filter)
      }
    }

    return { filters }
  } catch (error) {
    return {
      filters: [],
      error: `Invalid query: ${error instanceof Error ? error.message : 'Unknown error'}`,
    }
  }
}

function parseFilter(part: string): QueryFilter | null {
  // Match pattern: field:operator:value or field:value
  const match = part.match(/^(\w+):(>|<|>=|<=|=)?(.+)$/)

  if (!match) {
    return null
  }

  const [, field, op, rawValue] = match
  const mappedField = FIELD_MAPPINGS[field.toLowerCase()] || field

  // Determine operator
  let operator: QueryFilter['operator'] = 'eq'
  if (op === '>') operator = 'gt'
  else if (op === '<') operator = 'lt'
  else if (op === '>=') operator = 'gte'
  else if (op === '<=') operator = 'lte'

  // Parse value
  let value: string | number | boolean = rawValue.trim()

  // Handle wildcards
  if (typeof value === 'string' && value.includes('*')) {
    if (value.endsWith('*') && !value.startsWith('*')) {
      operator = 'startswith'
      value = value.slice(0, -1)
    } else if (value.startsWith('*') && !value.endsWith('*')) {
      operator = 'endswith'
      value = value.slice(1)
    } else {
      operator = 'contains'
      value = value.replace(/\*/g, '')
    }
  }

  // Parse duration values (e.g., 1000ms, 5s, 2m)
  if (field.toLowerCase() === 'duration' && typeof value === 'string') {
    const durationMatch = value.match(/^(\d+(?:\.\d+)?)(ms|s|m|h)?$/)
    if (durationMatch) {
      const [, num, unit = 'ms'] = durationMatch
      value = parseFloat(num) * (TIME_UNITS[unit] || 1)
    }
  }

  // Parse boolean values
  if (field.toLowerCase() === 'error' && typeof value === 'string') {
    value = value.toLowerCase() === 'true' || value === '1'
  }

  // Parse numbers
  if (typeof value === 'string' && !isNaN(Number(value))) {
    value = Number(value)
  }

  return {
    field: mappedField,
    operator,
    value,
  }
}

export function applyFilters(traces: any[], filters: QueryFilter[]): any[] {
  if (filters.length === 0) {
    return traces
  }

  return traces.filter(trace => {
    let result = true
    let lastCombinator: 'AND' | 'OR' = 'AND'

    for (const filter of filters) {
      const matches = matchesFilter(trace, filter)

      if (filter.combinator === 'OR') {
        result = result || matches
        lastCombinator = 'OR'
      } else {
        if (lastCombinator === 'OR') {
          result = result || matches
        } else {
          result = result && matches
        }
        lastCombinator = 'AND'
      }
    }

    return result
  })
}

function matchesFilter(trace: any, filter: QueryFilter): boolean {
  const value = trace[filter.field]
  const filterValue = filter.value

  switch (filter.operator) {
    case 'eq':
      return value === filterValue
    case 'gt':
      return value > filterValue
    case 'lt':
      return value < filterValue
    case 'gte':
      return value >= filterValue
    case 'lte':
      return value <= filterValue
    case 'contains':
      return String(value).toLowerCase().includes(String(filterValue).toLowerCase())
    case 'startswith':
      return String(value).toLowerCase().startsWith(String(filterValue).toLowerCase())
    case 'endswith':
      return String(value).toLowerCase().endsWith(String(filterValue).toLowerCase())
    default:
      return false
  }
}

export function buildQueryString(filters: QueryFilter[]): string {
  return filters
    .map((filter, index) => {
      let str = ''

      // Add combinator
      if (index > 0 && filter.combinator) {
        str += ` ${filter.combinator} `
      }

      // Reverse map field name
      const displayField = Object.entries(FIELD_MAPPINGS).find(
        ([, mapped]) => mapped === filter.field
      )?.[0] || filter.field

      // Build filter string
      let op = ''
      if (filter.operator === 'gt') op = '>'
      else if (filter.operator === 'lt') op = '<'
      else if (filter.operator === 'gte') op = '>='
      else if (filter.operator === 'lte') op = '<='
      else if (filter.operator === 'contains') op = ':'

      str += `${displayField}:${op}${filter.value}`

      // Add wildcards for pattern matching
      if (filter.operator === 'startswith') {
        str = `${displayField}:${filter.value}*`
      } else if (filter.operator === 'endswith') {
        str = `${displayField}:*${filter.value}`
      } else if (filter.operator === 'contains' && op === ':') {
        str = `${displayField}:*${filter.value}*`
      }

      return str
    })
    .join('')
}
