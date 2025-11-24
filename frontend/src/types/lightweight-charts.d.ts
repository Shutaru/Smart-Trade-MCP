declare module 'lightweight-charts' {
  export type UTCTimestamp = number
  export type DeepPartial<T> = Partial<T>
  export interface IChartApi {
    remove(): void
    applyOptions(opts: any): void
    addCandlestickSeries(opts?: any): any
    addLineSeries(opts?: any): any
  }
  export interface ISeriesApi<T> {
    setData(data: any[]): void
    setMarkers(markers: any[]): void
  }
  export function createChart(container: HTMLElement, options?: any): IChartApi
  export default createChart
}
