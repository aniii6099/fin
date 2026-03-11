import { useMemo } from 'react'

function resolveColor(value, thresholds) {
  if (value === null || value === undefined) return 'border-slate-500 text-slate-300'
  if (value <= thresholds.critical.low || value >= thresholds.critical.high) {
    return 'border-rose-500 text-rose-300'
  }
  if (value <= thresholds.warn.low || value >= thresholds.warn.high) {
    return 'border-amber-400 text-amber-300'
  }
  return 'border-emerald-400 text-emerald-300'
}

export default function VitalCard({ label, value, unit, icon: Icon, thresholds, stale }) {
  const style = useMemo(() => resolveColor(value, thresholds), [value, thresholds])

  return (
    <div className={`relative rounded-xl border bg-panel/90 p-5 ${style}`}>
      {stale ? <div className="absolute inset-0 rounded-xl bg-slate-900/55" /> : null}
      <div className="relative z-10">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm text-slate-200">{label}</span>
          {Icon ? <Icon size={18} /> : null}
        </div>
        <div className="flex items-end gap-2">
          <span className="text-3xl font-bold">{value ?? '--'}</span>
          <span className="text-sm">{unit}</span>
        </div>
      </div>
    </div>
  )
}
