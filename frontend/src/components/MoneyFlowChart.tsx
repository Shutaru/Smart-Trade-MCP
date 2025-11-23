import { useEffect, useRef } from 'react'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'

export default function MoneyFlowChart({ series }: { series: { time: string; value: number }[] }) {
  const ref = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const lineRef = useRef<ISeriesApi<'Line'> | null>(null)

  useEffect(() => {
    let ro: ResizeObserver | null = null
    let mounted = true

    async function init() {
      if (!ref.current) return

      let createChart: any
      try {
        const mod = await import('lightweight-charts')
        createChart = (mod && (mod.default || mod.createChart)) || mod
      } catch (e) {
        const shim = await import('../libs/lightweight-charts-shim')
        createChart = (shim && (shim.default)) || shim
      }

      chartRef.current = createChart(ref.current, { width: ref.current.clientWidth, height: 200, layout: { background: { color: '#fff' }, textColor: '#333' }, timeScale: { borderColor: '#eee' }, rightPriceScale: { borderColor: '#eee' } })
      if (chartRef.current) lineRef.current = chartRef.current.addLineSeries({ color: '#2b8efc', lineWidth: 2 })

      const data = series.map(s => ({ time: Math.floor(new Date(s.time).getTime() / 1000), value: s.value }))
      if (lineRef.current) lineRef.current.setData(data)

      ro = new ResizeObserver(() => chartRef.current && chartRef.current.applyOptions({ width: ref.current!.clientWidth }))
      ro.observe(ref.current)

      return () => {
        mounted = false
        if (ro && ref.current) ro.disconnect()
        chartRef.current?.remove()
        chartRef.current = null
      }
    }

    init()

    return () => {
      mounted = false
      if (ro && ref.current) ro.disconnect()
    }
  }, [])

  useEffect(() => {
    if (!lineRef.current) return
    const data = series.map(s => ({ time: Math.floor(new Date(s.time).getTime() / 1000), value: s.value }))
    if (lineRef.current) lineRef.current.setData(data)
  }, [series])

  return <div ref={ref} style={{ width: '100%' }} />
}
