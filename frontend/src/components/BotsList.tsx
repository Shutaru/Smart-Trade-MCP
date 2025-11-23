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
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6">
      <h3 className="text-2xl font-bold mb-4">Active Bots</h3>
      {agents.length === 0 ? (
        <div className="text-gray-500">No active bots</div>
      ) : (
        <div className="space-y-3">
          {agents.map((a) => (
            <div key={a.agent_id} className="flex items-center justify-between border rounded-lg p-3 hover:shadow-lg transition">
              <div>
                <div className="font-semibold">{a.strategy} - {a.symbol} ({a.timeframe})</div>
                <div className="text-sm text-gray-500">ID: {a.agent_id}</div>
              </div>
              <div className="text-right">
                <div className={`px-3 py-1 rounded-full text-sm ${a.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>{a.status}</div>
                <button
                  onClick={() => onSelect(a.agent_id)}
                  className="mt-2 ml-3 bg-primary-500 text-white px-4 py-2 rounded-lg hover:opacity-90"
                >
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
