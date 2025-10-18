import { useState, useCallback } from 'react'
import type { ToastProps } from '@/components/Toast'

let toastId = 0

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const addToast = useCallback(
    (message: string, type: ToastProps['type'] = 'info', duration = 5000) => {
      const id = `toast-${toastId++}`
      const onClose = (id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }

      setToasts((prev) => [...prev, { id, message, type, duration, onClose }])
    },
    []
  )

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return {
    toasts,
    addToast,
    removeToast,
    success: (message: string, duration?: number) => addToast(message, 'success', duration),
    error: (message: string, duration?: number) => addToast(message, 'error', duration),
    info: (message: string, duration?: number) => addToast(message, 'info', duration),
    warning: (message: string, duration?: number) => addToast(message, 'warning', duration),
  }
}
