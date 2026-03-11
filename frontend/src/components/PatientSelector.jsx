import { useEffect, useState } from 'react'

export default function PatientSelector({ selectedPatientId, onPatientChange }) {
  const [patients, setPatients] = useState([])

  useEffect(() => {
    let mounted = true

    const load = async () => {
      try {
        const res = await fetch('http://localhost:8000/patients')
        if (!res.ok) throw new Error('Failed to load patients')
        const list = await res.json()
        if (!mounted) return

        setPatients(list)
        if (!selectedPatientId && list.length > 0) {
          onPatientChange(list[0])
        }
      } catch (error) {
        console.error(error)
      }
    }

    load()
    return () => {
      mounted = false
    }
  }, [onPatientChange, selectedPatientId])

  return (
    <select
      className="rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-slate-100"
      value={selectedPatientId ?? ''}
      onChange={(e) => {
        const id = Number(e.target.value)
        const selected = patients.find((p) => p.id === id)
        if (selected) onPatientChange(selected)
      }}
    >
      {patients.length === 0 ? <option value="">No Patients</option> : null}
      {patients.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name} - Room {p.room_number}
        </option>
      ))}
    </select>
  )
}
