import { useEffect } from 'react'

function playBeep() {
  const AC = window.AudioContext || window.webkitAudioContext
  if (!AC) return
  const ctx = new AC()
  const oscillator = ctx.createOscillator()
  const gain = ctx.createGain()

  oscillator.type = 'square'
  oscillator.frequency.setValueAtTime(900, ctx.currentTime)
  gain.gain.setValueAtTime(0.001, ctx.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.35, ctx.currentTime + 0.02)
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4)

  oscillator.connect(gain)
  gain.connect(ctx.destination)
  oscillator.start()
  oscillator.stop(ctx.currentTime + 0.45)
  oscillator.onended = () => ctx.close()
}

export default function AlertBanner({ alert, patientName, onDismiss }) {
  useEffect(() => {
    if (alert?.alert_type === 'DISTURBANCE') {
      playBeep()
    }
  }, [alert])

  if (!alert || !alert.alert_type) return null

  if (alert.alert_type === 'DISTURBANCE') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-red-800/90">
        <div className="max-w-3xl rounded-xl border-4 border-red-200 bg-red-950/90 p-8 text-center">
          <h2 className="text-4xl font-black text-red-100">Device Disturbed - Possible Emergency Near Patient {patientName}</h2>
          <button className="mt-6 rounded bg-white px-5 py-2 font-semibold text-red-800" onClick={onDismiss}>
            Dismiss
          </button>
        </div>
      </div>
    )
  }

  const variants = {
    ANOMALY: 'border-amber-300 bg-amber-200 text-slate-900',
    NO_CONTACT_TIMEOUT: 'border-orange-300 bg-orange-300 text-slate-900',
    DEVICE_OFFLINE: 'border-slate-500 bg-slate-700 text-slate-100',
  }

  const text = {
    ANOMALY: alert.anomaly?.description ?? 'Anomaly detected in vitals',
    NO_CONTACT_TIMEOUT: 'Patient has not used sensor for 2+ minutes',
    DEVICE_OFFLINE: 'Device offline - check connection',
  }

  return (
    <div className={`fixed inset-x-0 top-0 z-40 border-b px-4 py-3 ${variants[alert.alert_type]}`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
        <span className="font-semibold">{text[alert.alert_type]}</span>
        <button className="rounded bg-white/80 px-3 py-1 text-sm font-bold text-slate-900" onClick={onDismiss}>
          Dismiss
        </button>
      </div>
    </div>
  )
}
