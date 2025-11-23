import { useEffect, useState, useRef } from 'react'
import BotsList from '../components/BotsList'
import TradingChart from '../components/TradingChart'
import MoneyFlowChart from '../components/MoneyFlowChart'

const API = 'http://localhost:8000/api/v1/paper'

export default function PaperDashboard() {
  const [agents, setAgents] = useState<any[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [details, setDetails] = useState<any | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    fetchAgents()
  }, [])

  async function fetchAgents() {
    const res = await fetch(`${API}/bots`)
    const data = await res.json()
    setAgents(data.agents || [])
  }

  async function selectAgent(id: string) {
    setSelected(id)
    const res = await fetch(`${API}/bots/${id}`)
    const data = await res.json()
    setDetails(data)

    // connect WS
    if (wsRef.current) {
      wsRef.current.close()
    }
    const ws = new WebSocket(`ws://localhost:8000/api/v1/paper/ws/paper/${id}`)
    ws.onopen = () => console.log('ws open')
    ws.onmessage = (ev) => {
      const payload = JSON.parse(ev.data)
      if (payload.type === 'snapshot') {
        setDetails({ agent: payload.agent, performance: payload.performance, trades: payload.trades })
      } else if (payload.type === 'event') {
        // append event or refresh
        const evt = payload.event
        if (evt['event_type'] === 'trade_open' || evt['event_type'] === 'trade_close') {
          fetch(`${API}/bots/${id}`).then(r => r.json()).then(d => setDetails(d))
        }
        // heartbeat or other events can update status
      }
    }
    wsRef.current = ws
  }

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [selected])

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-1">
          <BotsList agents={agents} onSelect={selectAgent} />
        </div>

        <div className="col-span-2">
          {selected && details ? (
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex items-start justify-between">
                <h2 className="text-2xl font-bold mb-4">Bot Details - {selected}</h2>
                <div className="text-right">
                  <div className="text-sm text-gray-500">Status: {details.agent?.status || 'unknown'}</div>
                  <div className="text-sm text-gray-400">PID: {details.agent?.pid || '-'}</div>
                </div>
              </div>


              <div className="grid grid-cols-1 gap-6">
                <TradingChart symbol={details.agent.symbol} timeframe={details.agent.timeframe} trades={details.trades || []} />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded">
                    <h3 className="font-semibold mb-2">Equity / Money Flow</h3>
                    <MoneyFlowChart series={(details.performance?.equity_series || [{ time: new Date().toISOString(), value: 0 }])} />
                  </div>

                  <div className="p-4 border rounded">
                    <h3 className="font-semibold mb-2">Trades</h3>
                    <div className="mt-2 max-h-64 overflow-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-left text-gray-600">
                            <th>Time</th>
                            <th>Side</th>
                            <th>Entry</th>
                            <th>Exit</th>
                            <th>PnL</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(details.trades || []).map((t: any) => (
                            <tr key={t.id} className="border-b">
                              <td className="py-2">{t.entry_time}</td>
                              <td>{t.direction}</td>
                              <td>{t.entry_price}</td>
                              <td>{t.exit_price || '-'}</td>
                              <td className={`font-bold ${t.pnl > 0 ? 'text-green-600' : 'text-red-600'}`}>{t.pnl || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                <div className="p-4 border rounded">
                  <h3 className="font-semibold mb-2">Summary</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-500">Total Trades</div>
                      <div className="text-lg font-bold">{details.performance?.total_trades || 0}</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-500">Win Rate</div>
                      <div className="text-lg font-bold">{details.performance?.win_rate || 0}%</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-sm text-gray-500">Total PnL</div>
                      <div className="text-lg font-bold">{details.performance?.total_pnl || 0}</div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-xl p-6">Select a bot to view details</div>
          )}
        </div>
      </div>
    </div>
  )
}
