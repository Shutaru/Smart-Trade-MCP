import { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts'

export default function MoneyFlowChart({ series }: { series: { time: string; value: number }[] }) {
  const ref = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const lineRef = useRef<ISeriesApi | null>(null)

  useEffect(() => {
    let ro: ResizeObserver | null = null

    async function init() {
      if (!ref.current) return

      const cs = getComputedStyle(document.documentElement)
      const textColor = (cs.getPropertyValue('--text') || '#333').trim()
      const bg = (cs.getPropertyValue('--panel') || '#fff').trim()

      chartRef.current = createChart(ref.current, { width: ref.current.clientWidth, height: 140, layout: { background: { color: bg }, textColor }, timeScale: { borderColor: '#eee' }, rightPriceScale: { borderColor: '#eee' } })
      if (chartRef.current) lineRef.current = chartRef.current.addLineSeries({ color: '#7c3aed', lineWidth: 2 })

      const data = series.map(s => ({ time: Math.floor(new Date(s.time).getTime() / 1000), value: s.value }))
      if (lineRef.current) lineRef.current.setData(data)

      ro = new ResizeObserver(() => chartRef.current && chartRef.current.applyOptions({ width: ref.current!.clientWidth }))
      ro.observe(ref.current)

      return () => {
        if (ro && ref.current) ro.disconnect()
        chartRef.current?.remove()
        chartRef.current = null
      }
    }

    init()

    return () => { if (ro && ref.current) ro.disconnect() }
  }, [])

  useEffect(() => {
    if (!lineRef.current) return
    const data = series.map(s => ({ time: Math.floor(new Date(s.time).getTime() / 1000), value: s.value }))
    if (lineRef.current) lineRef.current.setData(data)
  }, [series])

  return <div ref={ref} style={{ width: '100%' }} />
}
