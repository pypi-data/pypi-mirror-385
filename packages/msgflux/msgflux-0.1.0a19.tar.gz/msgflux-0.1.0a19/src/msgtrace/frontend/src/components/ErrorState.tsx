import { AlertCircle, RefreshCcw } from 'lucide-react'
import { Card, CardContent } from './Card'

interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorState({ title = 'Error', message, onRetry }: ErrorStateProps) {
  return (
    <Card>
      <CardContent className="py-12 flex flex-col items-center justify-center text-center space-y-4">
        <div className="p-3 rounded-full bg-red-500/10">
          <AlertCircle className="w-8 h-8 text-red-400" />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="text-sm text-gray-400 max-w-md">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg text-white transition-colors"
          >
            <RefreshCcw className="w-4 h-4" />
            Try Again
          </button>
        )}
      </CardContent>
    </Card>
  )
}

export function EmptyState({ message, icon: Icon }: { message: string; icon?: any }) {
  const DefaultIcon = AlertCircle

  return (
    <Card>
      <CardContent className="py-12 flex flex-col items-center justify-center text-center space-y-4">
        <div className="p-3 rounded-full bg-gray-800/50">
          {Icon ? <Icon className="w-8 h-8 text-gray-400" /> : <DefaultIcon className="w-8 h-8 text-gray-400" />}
        </div>
        <p className="text-gray-400">{message}</p>
      </CardContent>
    </Card>
  )
}
