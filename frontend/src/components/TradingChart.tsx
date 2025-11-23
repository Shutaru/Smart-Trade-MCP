import { useEffect, useRef } from 'react'
import createChart from 'lightweight-charts'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'

interface Trade {
  id: number
  entry_time: string
  exit_time?: string
  entry_price: number
  exit_price?: number
  direction: string
  pnl?: number
}

export default function TradingChart({ symbol, timeframe, trades }: { symbol: string; timeframe: string; trades: Trade[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const markersRef = useRef<any[]>([])

  // Fetch candles from API
  async function fetchCandles() {
    try {
      const qs = `symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(timeframe)}&limit=500`
      const res = await fetch(`/api/v1/market/candles?${qs}`)
      if (!res.ok) return []
      const data = await res.json()
      // Expect data.candles array of {time, open, high, low, close, volume}
      return data.candles || []
    } catch (e) {
      console.warn('Failed to fetch candles', e)
      return []
    }
  }

  useEffect(() => {
    let mounted = true
    async function init() {
      if (!containerRef.current) return

      // create chart
      chartRef.current = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height: 400,
        layout: { background: { color: '#ffffff' }, textColor: '#333' },
        grid: { vertLines: { color: '#f0f0f0' }, horzLines: { color: '#f0f0f0' } },
        rightPriceScale: { borderColor: '#eee' },
        timeScale: { borderColor: '#eee' }
      })

      candleSeriesRef.current = chartRef.current.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350'
      })

      const candles = await fetchCandles()
      if (!mounted) return

      // convert times: if ISO strings convert to unix seconds
      const formatted = candles.map((c: any) => {
        let time: number | string = c.time
        if (typeof time === 'string' && isNaN(Number(time))) {
          time = Math.floor(new Date(time).getTime() / 1000)
        }
        return {
          time,
          open: Number(c.open),
          high: Number(c.high),
          low: Number(c.low),
          close: Number(c.close)
        }
      })

      candleSeriesRef.current?.setData(formatted)

      // markers from trades
      if (trades && trades.length > 0) {
        const markers = trades.flatMap((t: any) => {
          const marks: any[] = []
          try {
            const entryTs = Math.floor(new Date(t.entry_time).getTime() / 1000)
            marks.push({
              time: entryTs,
              position: t.direction === 'long' ? 'belowBar' : 'aboveBar',
              color: t.direction === 'long' ? 'green' : 'red',
              shape: 'arrowUp',
              text: `Entry ${t.entry_price}`
            })
            if (t.exit_time) {
              const exitTs = Math.floor(new Date(t.exit_time).getTime() / 1000)
              marks.push({
                time: exitTs,
                position: t.direction === 'long' ? 'aboveBar' : 'belowBar',
                color: t.pnl && t.pnl > 0 ? 'lime' : 'red',
                shape: 'arrowDown',
                text: `Exit ${t.exit_price} (${t.pnl ? t.pnl.toFixed(2) : ''})`
              })
            }
          } catch (e) {
            // ignore
          }
          return marks
        })
        markersRef.current = markers
        if (candleSeriesRef.current) candleSeriesRef.current.setMarkers(markers)
      }

      // resize observer
      const ro = new ResizeObserver(() => {
        if (containerRef.current && chartRef.current) {
          chartRef.current.applyOptions({ width: containerRef.current.clientWidth })
        }
      })
      ro.observe(containerRef.current)

      return () => {
        mounted = false
        ro.disconnect()
        chartRef.current?.remove()
        chartRef.current = null
      }
    }

    init()
  }, [symbol, timeframe])

  // update markers when trades change
  useEffect(() => {
    if (!candleSeriesRef.current) return
    if (!trades) return
    const markers = trades.flatMap((t: any) => {
      const marks: any[] = []
      try {
        const entryTs = Math.floor(new Date(t.entry_time).getTime() / 1000)
        marks.push({
          time: entryTs,
          position: t.direction === 'long' ? 'belowBar' : 'aboveBar',
          color: t.direction === 'long' ? 'green' : 'red',
          shape: 'arrowUp',
          text: `Entry ${t.entry_price}`
        })
        if (t.exit_time) {
          const exitTs = Math.floor(new Date(t.exit_time).getTime() / 1000)
          marks.push({
            time: exitTs,
            position: t.direction === 'long' ? 'aboveBar' : 'belowBar',
            color: t.pnl && t.pnl > 0 ? 'lime' : 'red',
            shape: 'arrowDown',
            text: `Exit ${t.exit_price} (${t.pnl ? t.pnl.toFixed(2) : ''})`
          })
        }
      } catch (e) {}
      return marks
    })
    markersRef.current = markers
    if (candleSeriesRef.current) candleSeriesRef.current.setMarkers(markers)
  }, [trades])

  return <div ref={containerRef} style={{ width: '100%', height: 400 }} />
}
