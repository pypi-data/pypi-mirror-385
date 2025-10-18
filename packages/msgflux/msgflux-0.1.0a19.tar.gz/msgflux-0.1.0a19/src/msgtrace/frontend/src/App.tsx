import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useWebSocket } from './hooks/useWebSocket'
import { useToast } from './hooks/useToast'
import { ToastContainer } from './components/Toast'
import Layout from './components/Layout'
import Dashboard from './views/Dashboard'
import TraceList from './views/TraceList'
import TraceDetail from './views/TraceDetail'
import TraceCompare from './views/TraceCompare'
import Alerts from './views/Alerts'
import AlertHistory from './views/AlertHistory'
import Performance from './views/Performance'

function App() {
  const { toasts, success, error, removeToast } = useToast()

  // Initialize WebSocket connection with notifications
  useWebSocket({
    onTraceCreated: (traceId) => {
      success(`New trace captured: ${traceId.substring(0, 16)}...`, 3000)
    },
    onAlertTriggered: (alertData) => {
      const severity = alertData.severity
      const message = `🚨 Alert: ${alertData.alert_name}`

      // Show different toast types based on severity
      if (severity === 'critical' || severity === 'error') {
        error(message, 5000)
      } else {
        success(message, 4000)
      }
    },
  })

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="traces" element={<TraceList />} />
            <Route path="traces/compare" element={<TraceCompare />} />
            <Route path="traces/:traceId" element={<TraceDetail />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="alerts/history" element={<AlertHistory />} />
            <Route path="performance" element={<Performance />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </>
  )
}

export default App
