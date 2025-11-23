import { useEffect, useState, useRef } from 'react'
import BotsList from '../components/BotsList'
import BotModal from '../components/BotModal'
import { useTheme } from '../contexts/ThemeContext'



const API = '/api/v1/paper'

const API_BACKEND = 'http://127.0.0.1:8000/api/v1/paper'



export default function PaperDashboard() {

  const [agents, setAgents] = useState<any[]>([])

  const [selected, setSelected] = useState<string | null>(null)

  const [details, setDetails] = useState<any | null>(null)

  const [lastFocusedEl, setLastFocusedEl] = useState<HTMLElement | null>(null)

  const wsRef = useRef<WebSocket | null>(null)

  const { theme, toggle } = useTheme()



  useEffect(() => {

    fetchAgents()

    const interval = setInterval(fetchAgents, 5000)

    return () => clearInterval(interval)

  }, [])



  async function fetchWithFallback(path: string) {

    const backendPath = path.replace('/api/v1/paper', API_BACKEND)

    try {

      const r1 = await fetch(backendPath)

      if (r1.ok) return r1

    } catch (e) {}

    try {

      const r2 = await fetch(path)

      if (r2.ok) return r2

      return r2

    } catch (e) { throw e }

  }



  async function fetchAgents() {

    try {

      let res = await fetchWithFallback(`${API}/bots/active`)

      if (!res || !res.ok) res = await fetchWithFallback(`${API}/bots`)

      if (!res) throw new Error('No response from API')

      const data = await res.json()

      if (Array.isArray(data)) setAgents(data)

      else if (data && Array.isArray(data.agents)) setAgents(data.agents)

      else if (data && Array.isArray(data.items)) setAgents(data.items)

      else setAgents([])

    } catch (e: any) {

      console.error('Failed to fetch agents', e)

      setAgents([])

    }

  }



  async function selectAgent(id: string) {

    // store current focus to return later

    try {

      setLastFocusedEl(document.activeElement as HTMLElement | null)

    } catch {}

    

    try {

      let res = await fetchWithFallback(`${API}/bots/${id}`)

      if (!res || !res.ok) throw new Error('Failed to fetch agent details')

      const data = await res.json()

      if (data && data.agent) setDetails(data)

      else setDetails({ agent: data, performance: {} })

      setSelected(id)

    } catch (e: any) {

      console.warn('Failed to fetch agent details', e)

      setDetails(null)

    }



    // open WS

    if (wsRef.current) { wsRef.current.close() }

    try {

      const host = window.location.hostname || '127.0.0.1'

      const wsUrl = `ws://${host}:8000/api/v1/paper/ws/paper/${id}`

      const ws = new WebSocket(wsUrl)

      ws.onmessage = (ev) => {

        const payload = JSON.parse(ev.data)

        if (payload.type === 'snapshot') setDetails({ agent: payload.agent, performance: payload.performance, trades: payload.trades })

      }

      wsRef.current = ws

    } catch (e) { console.warn('WS failed', e) }

  }



  function closeModal() {

    setSelected(null)

    setDetails(null)

    if (wsRef.current) { wsRef.current.close(); wsRef.current = null }

    // restore focus

    try {

      if (lastFocusedEl && typeof lastFocusedEl.focus === 'function') {

        lastFocusedEl.focus()

      }

    } catch {}

    setLastFocusedEl(null)

  }



  return (

    <div className="container-wide">

      <div className="flex items-center justify-between mb-6">

        <h1 className="text-2xl font-bold">SmartTrade - Paper Dashboard</h1>

        <div className="flex items-center gap-3">

          <div className="text-sm small-muted">Theme: {theme}</div>

          <button onClick={toggle} className="btn-theme">Toggle Theme</button>

        </div>

      </div>



      <div className="grid-3">

        <aside className="sidebar">

          <BotsList agents={agents} onSelect={selectAgent} />

        </aside>



        <main className="content">

          <div className="card-panel">

            <div className="text-center small-muted">

              Click a bot to view details

            </div>

          </div>

        </main>

      </div>



      <BotModal open={!!selected} onClose={closeModal} details={details} />

    </div>

  )

}

