import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function LiveHeartRateChart({ points }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950/80 p-4">
      <h3 className="mb-2 text-lg font-semibold">Heart Rate Trend</h3>
      <div className="h-72 w-full">
        <ResponsiveContainer>
          <LineChart data={points}>
            <XAxis dataKey="time" tick={{ fill: '#cbd5e1', fontSize: 12 }} tickLine={false} axisLine={false} />
            <YAxis domain={[40, 170]} tick={{ fill: '#cbd5e1', fontSize: 12 }} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '10px' }}
            />
            <Line type="monotone" dataKey="hr" stroke="#14b8a6" strokeWidth={3} dot={false} connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
