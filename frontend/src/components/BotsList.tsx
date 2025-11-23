import { useState, useMemo } from 'react'

interface AgentSummary {
  agent_id: string
  symbol: string
  timeframe: string
  strategy: string
  status: string
  total_trades?: number
  total_pnl?: number
  performance?: { equity_series?: { time: string; value: number }[] }
}

export default function BotsList({ agents, onSelect }: { agents: AgentSummary[]; onSelect: (id: string) => void }) {
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => {
    if (!query) return agents
    const q = query.toLowerCase()
    return agents.filter(a => `${a.strategy} ${a.symbol} ${a.timeframe}`.toLowerCase().includes(q))
  }, [agents, query])

  const loading = agents === null || agents === undefined

  return (
    <div className="card-panel full-width-list">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Active Bots</h3>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search bots..."
          className="px-3 py-1 rounded-md border" />
      </div>

      {loading ? (
        <div className="space-y-3">
          <div className="h-16 bg-gray-100 rounded animate-pulse" />
          <div className="h-16 bg-gray-100 rounded animate-pulse" />
          <div className="h-16 bg-gray-100 rounded animate-pulse" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-sm small-muted">No active bots</div>
      ) : (
        <div className="space-y-2">
          {filtered.map((a) => (
            <div
              key={a.agent_id}
              className="w-full p-4 border rounded-lg hover:shadow-md transition cursor-pointer flex items-center gap-4"
              role="button"
              tabIndex={0}
              title={a.agent_id}
              onClick={() => onSelect(a.agent_id)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onSelect(a.agent_id) }}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div className="font-semibold truncate text-lg">{a.symbol} <span className="text-sm small-muted">| {a.strategy}</span></div>
                  <div className="ml-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${a.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>{a.status}</span>
                  </div>
                </div>
                <div className="text-sm small-muted break-words mt-1">{a.timeframe} - ID: <span className="font-mono text-xs break-all">{a.agent_id}</span></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
