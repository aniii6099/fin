import { useEffect, useMemo, useState } from 'react'

export default function DeviceStatusBar({
  isConnected,
  status,
  contact,
  lastReadingTimestamp,
}) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const interval = window.setInterval(() => {
      if (!lastReadingTimestamp) {
        setElapsed(0)
        return
      }
      const seconds = Math.max(
        0,
        Math.floor((Date.now() - new Date(lastReadingTimestamp).getTime()) / 1000)
      )
      setElapsed(seconds)
    }, 1000)

    return () => window.clearInterval(interval)
  }, [lastReadingTimestamp])

  const barIsCritical = useMemo(() => status === 'DEVICE_OFFLINE', [status])

  const deviceOnline = isConnected && status !== 'DEVICE_OFFLINE'
  const sensorActive = contact && status === 'ACTIVE'

  return (
    <div
      className={`mb-4 rounded-lg border px-4 py-3 ${
        barIsCritical
          ? 'border-rose-400 bg-rose-900/70'
          : 'border-slate-700 bg-slate-900/70'
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className={`h-3 w-3 rounded-full ${deviceOnline ? 'bg-emerald-400' : 'bg-rose-500'}`} />
          Device: {deviceOnline ? 'Online' : 'Offline'}
        </div>
        <div className="flex items-center gap-2">
          <span className={`h-3 w-3 rounded-full ${sensorActive ? 'bg-emerald-400' : 'bg-amber-400'}`} />
          Sensor Contact: {sensorActive ? 'Active' : 'Waiting'}
        </div>
        <div>Last Reading: {elapsed}s ago</div>
      </div>
    </div>
  )
}
