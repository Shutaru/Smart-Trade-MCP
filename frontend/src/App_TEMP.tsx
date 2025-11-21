import { useEffect, useState } from 'react'
import './App.css'

interface Strategy {
  strategy: string
  total_return: number
  total_trades: number
  win_rate: number
  sharpe_ratio: number
  max_drawdown_pct: number
}

interface Stats {
  total_strategies: number
  regime_periods: number
  total_candles: number
  data_coverage_days: number
}

interface Comparison {
  best_single: {
    strategy: string
    total_return: number
    total_trades: number
    win_rate: number
  }
  regime_aware: {
    total_return: number
    total_trades: number
  }
  improvement: number
}

const API_URL = 'http://localhost:8000/api'

function App() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [regimeDistribution, setRegimeDistribution] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const [strategiesRes, statsRes, comparisonRes, regimeRes] = await Promise.all([
          fetch(`${API_URL}/strategies/top/10`),
          fetch(`${API_URL}/stats`),
          fetch(`${API_URL}/comparison`),
          fetch(`${API_URL}/regime/distribution`)
        ])

        if (!strategiesRes.ok) throw new Error('Failed to fetch strategies')

        setStrategies(await strategiesRes.json())
        setStats(await statsRes.json())
        setComparison(await comparisonRes.json())
        setRegimeDistribution(await regimeRes.json())
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
        console.error('Error fetching data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-2xl animate-pulse">Loading Dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-500 text-white p-8 rounded-2xl shadow-2xl max-w-md">
          <h2 className="text-2xl font-bold mb-4">?? Error</h2>
          <p className="mb-4">{error}</p>
          <p className="text-sm opacity-90">Make sure the backend API is running on port 8000</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-white text-red-500 px-6 py-2 rounded-lg font-bold hover:bg-gray-100 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <header className="bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-2xl shadow-2xl p-10 mb-8">
          <h1 className="text-5xl font-bold mb-2">?? Smart Trade MCP</h1>
          <p className="text-xl opacity-90">Professional Trading Dashboard</p>
        </header>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <StatCard label="Strategies Tested" value={stats.total_strategies} />
            <StatCard label="Data Coverage" value={stats.data_coverage_days} unit="days" />
            <StatCard label="Total Candles" value={stats.total_candles.toLocaleString()} />
            <StatCard label="Regime Periods" value={stats.regime_periods} />
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-primary-600 mb-6 pb-3 border-b-4 border-primary-500">
            ?? TOP 10 Strategies
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-primary-500 to-primary-600 text-white">
                <tr>
                  <th className="px-6 py-4 text-left rounded-tl-lg">Rank</th>
                  <th className="px-6 py-4 text-left">Strategy</th>
                  <th className="px-6 py-4 text-left">Return</th>
                  <th className="px-6 py-4 text-left">Trades</th>
                  <th className="px-6 py-4 text-left">Win Rate</th>
                  <th className="px-6 py-4 text-left">Sharpe</th>
                  <th className="px-6 py-4 text-left rounded-tr-lg">Max DD</th>
                </tr>
              </thead>
              <tbody>
                {strategies.map((strategy, index) => (
                  <tr
                    key={strategy.strategy}
                    className={`border-b hover:bg-purple-50 transition-colors ${
                      index % 2 === 0 ? 'bg-gray-50' : 'bg-white'
                    }`}
                  >
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-white font-bold ${
                          index === 0
                            ? 'bg-gradient-to-br from-yellow-400 to-orange-500 shadow-lg'
                            : index === 1
                            ? 'bg-gradient-to-br from-gray-300 to-gray-500 shadow-lg'
                            : index === 2
                            ? 'bg-gradient-to-br from-orange-400 to-orange-700 shadow-lg'
                            : 'bg-gradient-to-br from-purple-400 to-purple-600'
                        }`}
                      >
                        {index + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-800">{strategy.strategy}</td>
                    <td
                      className={`px-6 py-4 font-bold ${
                        strategy.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {strategy.total_return.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 text-gray-700">{strategy.total_trades}</td>
                    <td className="px-6 py-4 text-gray-700">{strategy.win_rate.toFixed(1)}%</td>
                    <td className="px-6 py-4 text-gray-700">{strategy.sharpe_ratio.toFixed(2)}</td>
                    <td className="px-6 py-4 text-red-600 font-semibold">
                      {strategy.max_drawdown_pct.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-primary-600 mb-6 pb-3 border-b-4 border-primary-500">
            ?? Market Regime Distribution
          </h2>
          <div className="flex flex-wrap gap-3">
            {Object.entries(regimeDistribution).map(([regime, pct]) => (
              <span
                key={regime}
                className={`inline-block px-6 py-3 rounded-full text-white font-bold text-lg shadow-lg ${
                  regime === 'VOLATILE'
                    ? 'bg-purple-600 hover:bg-purple-700'
                    : regime === 'TRENDING_UP'
                    ? 'bg-green-600 hover:bg-green-700'
                    : regime === 'TRENDING_DOWN'
                    ? 'bg-red-600 hover:bg-red-700'
                    : regime === 'RANGING'
                    ? 'bg-orange-500 hover:bg-orange-600'
                    : 'bg-gray-600 hover:bg-gray-700'
                } transition-colors cursor-default`}
              >
                {regime}: {pct}%
              </span>
            ))}
          </div>
        </div>

        {comparison && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gradient-to-br from-green-500 to-green-700 text-white rounded-2xl shadow-xl p-8 transform hover:scale-105 transition-transform">
              <h3 className="text-2xl font-bold mb-6">?? Best Single Strategy</h3>
              <div className="space-y-4">
                <Metric label="Strategy" value={comparison.best_single.strategy} />
                <Metric
                  label="Total Return"
                  value={`${comparison.best_single.total_return.toFixed(2)}%`}
                />
                <Metric label="Total Trades" value={comparison.best_single.total_trades} />
                <Metric
                  label="Win Rate"
                  value={`${comparison.best_single.win_rate.toFixed(1)}%`}
                />
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-600 to-gray-800 text-white rounded-2xl shadow-xl p-8 transform hover:scale-105 transition-transform">
              <h3 className="text-2xl font-bold mb-6">?? Regime-Aware Strategy</h3>
              <div className="space-y-4">
                <Metric
                  label="Total Return"
                  value={`${comparison.regime_aware.total_return.toFixed(2)}%`}
                />
                <Metric label="Total Trades" value={comparison.regime_aware.total_trades} />
                <Metric
                  label="Improvement"
                  value={`${comparison.improvement.toFixed(2)}%`}
                  valueClass={comparison.improvement >= 0 ? 'text-green-300' : 'text-red-300'}
                />
              </div>
            </div>
          </div>
        )}

        <footer className="text-center text-white opacity-75 mt-12">
          <p className="text-lg">Smart Trade MCP - Autonomous Trading System</p>
          <p className="text-sm mt-2">{new Date().toLocaleString()}</p>
        </footer>
      </div>
    </div>
  )
}

function StatCard({ label, value, unit }: { label: string; value: number | string; unit?: string }) {
  return (
    <div className="bg-gradient-to-br from-primary-500 to-primary-600 text-white rounded-xl shadow-lg p-6 hover:shadow-2xl hover:-translate-y-1 transition-all cursor-default">
      <div className="text-sm opacity-90 mb-2">{label}</div>
      <div className="text-4xl font-bold">{value}</div>
      {unit && <div className="text-lg opacity-80 mt-1">{unit}</div>}
    </div>
  )
}

function Metric({
  label,
  value,
  valueClass = 'text-white'
}: {
  label: string
  value: string | number
  valueClass?: string
}) {
  return (
    <div className="flex justify-between items-center border-b border-white border-opacity-20 pb-2">
      <span className="opacity-90">{label}:</span>
      <span className={`font-bold text-xl ${valueClass}`}>{value}</span>
    </div>
  )
}

export default App
