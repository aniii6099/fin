const colorByLevel = {
  LOW: 'bg-emerald-600 text-emerald-50',
  MEDIUM: 'bg-amber-500 text-slate-900',
  HIGH: 'bg-rose-600 text-rose-50 animate-pulse',
}

export default function RiskBadge({ risk }) {
  if (!risk) {
    return <div className="rounded-xl border border-slate-700 bg-panel/70 px-4 py-3">No risk data</div>
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-panel/70 px-4 py-3 text-right">
      <span className={`rounded-full px-3 py-1 text-xs font-bold ${colorByLevel[risk.risk_level]}`}>
        {risk.risk_level}
      </span>
      <p className="mt-2 max-w-xs text-xs text-slate-200">{risk.reason}</p>
    </div>
  )
}
