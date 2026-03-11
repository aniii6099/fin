import { Hand } from 'lucide-react'

export default function AwaitingReading() {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-xl border border-slate-700 bg-panel/70 p-8 text-center">
      <div className="mb-4 rounded-full bg-slate-900 p-6 text-amber-300 shadow-lg animate-pulseSlow">
        <Hand size={64} />
      </div>
      <h2 className="text-2xl font-bold">Place finger on sensor to begin reading</h2>
      <p className="mt-2 text-slate-300">MAX30102 contact is required for HR and SpO2 capture.</p>
    </div>
  )
}
