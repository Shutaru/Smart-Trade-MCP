import { useState, useMemo } from 'react'

interface AgentSummary {
  agent_id: string
  symbol: string
  timeframe: string
  strategy: string
  status: string
  total_trades?: number
  total_pnl?: number
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
    <div>
      <div className="card-panel">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Active Bots</h3>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search bots..."
            className="px-3 py-1 rounded-md border" />
        </div>

        {loading ? (
          <div className="space-y-2">
            <div className="h-12 bg-gray-100 rounded animate-pulse" />
            <div className="h-12 bg-gray-100 rounded animate-pulse" />
            <div className="h-12 bg-gray-100 rounded animate-pulse" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-sm small-muted">No active bots</div>
        ) : (
          <div className="space-y-3">
            {filtered.map((a) => (
              <div
                key={a.agent_id}
                className="p-3 border rounded-lg hover:shadow-md transition cursor-pointer bg-gradient-to-tr from-white/2 to-transparent"
                role="button"
                tabIndex={0}
                onClick={() => onSelect(a.agent_id)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onSelect(a.agent_id) }}
              >
                <div className="font-semibold">{a.strategy} - <span className="text-primary">{a.symbol}</span> <span className="text-sm small-muted">({a.timeframe})</span></div>
                <div className="text-sm small-muted">ID: {a.agent_id}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
