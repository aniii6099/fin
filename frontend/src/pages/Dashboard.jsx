import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, HeartPulse, Thermometer } from 'lucide-react'

import AlertBanner from '../components/AlertBanner'
import AwaitingReading from '../components/AwaitingReading'
import DeviceStatusBar from '../components/DeviceStatusBar'
import LiveHeartRateChart from '../components/LiveHeartRateChart'
import PatientSelector from '../components/PatientSelector'
import RiskBadge from '../components/RiskBadge'
import VitalCard from '../components/VitalCard'
import useWebSocket from '../hooks/useWebSocket'

export default function Dashboard() {
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [chartPoints, setChartPoints] = useState([])
  const [activeAlert, setActiveAlert] = useState(null)
  const [alertsList, setAlertsList] = useState([])

  const patientId = selectedPatient?.id ?? null
  const { data, status, isConnected } = useWebSocket(patientId)

  const refreshAlerts = useCallback(async () => {
    if (!patientId) return
    try {
      const res = await fetch(`http://localhost:8000/patients/${patientId}/alerts`)
      if (!res.ok) return
      const list = await res.json()
      setAlertsList(list.slice(0, 5))
    } catch (error) {
      console.error(error)
    }
  }, [patientId])

  useEffect(() => {
    setChartPoints([])
    setActiveAlert(null)
    setAlertsList([])
    refreshAlerts()
  }, [patientId, refreshAlerts])

  useEffect(() => {
    if (status === 'ACTIVE' && data?.vitals?.hr && data?.vitals?.timestamp) {
      const point = { time: new Date(data.vitals.timestamp).toLocaleTimeString(), hr: Number(data.vitals.hr) }
      setChartPoints((prev) => [...prev, point].slice(-60))
    } else if (status === 'AWAITING_READING') {
      setChartPoints((prev) => [...prev, { time: new Date().toLocaleTimeString(), hr: null }].slice(-60))
    }

    if (data?.alert_type) {
      setActiveAlert(data)
      refreshAlerts()
    }
  }, [data, status, refreshAlerts])

  const dismissAlert = useCallback(async () => {
    if (activeAlert?.alert_id) {
      try {
        await fetch(`http://localhost:8000/alerts/${activeAlert.alert_id}/resolve`, { method: 'PATCH' })
      } catch (error) {
        console.error(error)
      }
    }
    setActiveAlert(null)
    refreshAlerts()
  }, [activeAlert, refreshAlerts])

  const vitals = useMemo(() => data?.vitals ?? null, [data])

  return (
    <div className="min-h-screen p-4 md:p-8">
      <AlertBanner alert={activeAlert} patientName={selectedPatient?.name ?? 'Unknown'} onDismiss={dismissAlert} />

      <DeviceStatusBar
        isConnected={isConnected}
        status={status}
        contact={Boolean(data?.contact)}
        lastReadingTimestamp={vitals?.timestamp}
      />

      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <div>
          <h1 className="text-2xl font-bold">HealTech Stationary Monitor</h1>
          <p className="text-sm text-slate-300">Patient bedside sensor dashboard</p>
        </div>

        <PatientSelector selectedPatientId={patientId} onPatientChange={setSelectedPatient} />

        <RiskBadge risk={data?.risk} />
      </div>

      {status === 'DEVICE_OFFLINE' ? (
        <div className="rounded-xl border border-rose-400 bg-rose-950/70 p-10 text-center text-xl font-bold text-rose-100">
          Device offline - check ESP32 power and network
        </div>
      ) : null}

      {status === 'AWAITING_READING' ? <AwaitingReading /> : null}

      {status === 'ACTIVE' ? (
        <>
          <div className="mb-5 grid grid-cols-1 gap-4 md:grid-cols-3">
            <VitalCard
              label="Heart Rate"
              value={vitals?.hr}
              unit="bpm"
              icon={HeartPulse}
              thresholds={{ warn: { low: 60, high: 110 }, critical: { low: 45, high: 130 } }}
              stale={!data?.contact}
            />
            <VitalCard
              label="SpO2"
              value={vitals?.spo2}
              unit="%"
              icon={Activity}
              thresholds={{ warn: { low: 94, high: 100 }, critical: { low: 89, high: 100 } }}
              stale={!data?.contact}
            />
            <VitalCard
              label="Temperature"
              value={vitals?.temp}
              unit="C"
              icon={Thermometer}
              thresholds={{ warn: { low: 35.5, high: 38.0 }, critical: { low: 34.5, high: 39.0 } }}
              stale={!data?.contact}
            />
          </div>

          <LiveHeartRateChart points={chartPoints} />
        </>
      ) : null}

      <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <h3 className="mb-3 text-lg font-semibold">Last 5 Alerts</h3>
        {alertsList.length === 0 ? (
          <p className="text-slate-300">No alerts yet.</p>
        ) : (
          <div className="space-y-2">
            {alertsList.map((alert) => (
              <div key={alert.id} className="rounded-lg border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-semibold">{alert.alert_type}</span>
                  <span className="text-xs text-slate-300">{new Date(alert.timestamp).toLocaleString()}</span>
                </div>
                <p className="text-slate-200">{alert.message}</p>
                <p className="text-xs text-slate-400">Resolved: {alert.resolved ? 'Yes' : 'No'}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
