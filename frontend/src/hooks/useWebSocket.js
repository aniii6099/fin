import { useEffect, useRef, useState } from 'react'

const INITIAL_DATA = {
  patient_id: null,
  status: 'AWAITING_READING',
  vitals: null,
  contact: false,
  disturbance: null,
  anomaly: null,
  risk: null,
  alert_type: null,
  alert_id: null,
  seconds_since_contact: 0,
}

export default function useWebSocket(patientId) {
  const [data, setData] = useState(INITIAL_DATA)
  const [status, setStatus] = useState('AWAITING_READING')
  const [isConnected, setIsConnected] = useState(false)
  const [secondsSinceContact, setSecondsSinceContact] = useState(0)

  const socketRef = useRef(null)
  const retryTimerRef = useRef(null)

  useEffect(() => {
    setData(INITIAL_DATA)
    setStatus('AWAITING_READING')
    setSecondsSinceContact(0)

    if (!patientId) {
      return undefined
    }

    let active = true

    const connect = () => {
      const ws = new WebSocket(`ws://localhost:8000/ws/${patientId}`)
      socketRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data)
          setData(parsed)
          setStatus(parsed.status ?? 'AWAITING_READING')
          setSecondsSinceContact(parsed.seconds_since_contact ?? 0)
        } catch (error) {
          console.error('Invalid websocket payload', error)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        if (active) {
          retryTimerRef.current = window.setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => ws.close()
    }

    connect()

    return () => {
      active = false
      setIsConnected(false)
      if (retryTimerRef.current) {
        window.clearTimeout(retryTimerRef.current)
      }
      if (socketRef.current) {
        socketRef.current.close()
      }
    }
  }, [patientId])

  return { data, status, isConnected, secondsSinceContact }
}
