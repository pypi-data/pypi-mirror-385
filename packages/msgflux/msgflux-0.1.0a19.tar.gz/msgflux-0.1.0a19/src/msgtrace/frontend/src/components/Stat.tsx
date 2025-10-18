import { Card, CardContent } from './Card'
import { Tooltip } from './Tooltip'
import type { LucideIcon } from 'lucide-react'

interface StatProps {
  label: string
  value: string | number
  icon: LucideIcon
  trend?: {
    value: number
    positive: boolean
  }
  tooltip?: string
}

export default function Stat({ label, value, icon: Icon, trend, tooltip }: StatProps) {
  const content = (
    <Card>
      <CardContent className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {trend && (
            <p className={`text-sm mt-1 ${trend.positive ? 'text-green-500' : 'text-red-500'}`}>
              {trend.positive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </p>
          )}
        </div>
        <div className="p-3 rounded-lg bg-primary-500/10">
          <Icon className="w-6 h-6 text-primary-500" />
        </div>
      </CardContent>
    </Card>
  )

  if (tooltip) {
    return <Tooltip content={tooltip}>{content}</Tooltip>
  }

  return content
}
