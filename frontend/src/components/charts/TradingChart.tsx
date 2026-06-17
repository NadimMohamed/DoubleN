'use client'
import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { marketApi } from '@/lib/api'
import type { KlineData } from '@/types'

interface ChartProps {
  symbol: string
  interval?: string
  height?: number
}

const INTERVALS = ['1m','5m','15m','1h','4h','1d']

export function TradingChart({ symbol, interval: defaultInterval = '1h', height = 400 }: ChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  const candleSeriesRef = useRef<any>(null)
  const [activeInterval, setActiveInterval] = useState(defaultInterval)

  const { data: klines, isLoading } = useQuery({
    queryKey: ['klines', symbol, activeInterval],
    queryFn: () => marketApi.getKlines(symbol, activeInterval, 300),
    refetchInterval: 60_000,
    staleTime: 30_000,
  })

  // Initialize chart
  useEffect(() => {
    if (!containerRef.current) return

    let chart: any = null

    const initChart = async () => {
      const { createChart, ColorType, CrosshairMode } = await import('lightweight-charts')
      if (!containerRef.current) return

      chart = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height,
        layout: {
          background: { type: ColorType.Solid, color: '#0f1f35' },
          textColor: '#94a3b8',
        },
        grid: {
          vertLines: { color: '#1e3a57', style: 1 },
          horzLines: { color: '#1e3a57', style: 1 },
        },
        crosshair: { mode: CrosshairMode.Normal },
        rightPriceScale: {
          borderColor: '#1e3a57',
          textColor: '#94a3b8',
        },
        timeScale: {
          borderColor: '#1e3a57',
          timeVisible: true,
          secondsVisible: false,
        },
        handleScroll: true,
        handleScale: true,
      })

      const candleSeries = chart.addCandlestickSeries({
        upColor: '#00C48C',
        downColor: '#FF4757',
        borderUpColor: '#00C48C',
        borderDownColor: '#FF4757',
        wickUpColor: '#00C48C',
        wickDownColor: '#FF4757',
      })

      chartRef.current = chart
      candleSeriesRef.current = candleSeries

      // Responsive resize
      const ro = new ResizeObserver((entries) => {
        if (entries[0] && chart) {
          chart.applyOptions({ width: entries[0].contentRect.width })
        }
      })
      ro.observe(containerRef.current)
      return () => ro.disconnect()
    }

    const cleanup = initChart()
    return () => {
      cleanup.then(() => {})
      if (chart) chart.remove()
      chartRef.current = null
      candleSeriesRef.current = null
    }
  }, [height])

  // Update data when klines change
  useEffect(() => {
    if (!klines || !candleSeriesRef.current) return

    const formatted = klines.map((k: KlineData) => ({
      time: Math.floor(k.open_time / 1000) as any,
      open: k.open,
      high: k.high,
      low: k.low,
      close: k.close,
    }))

    candleSeriesRef.current.setData(formatted)
    chartRef.current?.timeScale().fitContent()
  }, [klines])

  return (
    <div className="card flex flex-col overflow-hidden">
      {/* Chart toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-panel-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-white">{symbol.replace('USDT', '/USDT')}</span>
          <span className="text-xs text-slate">Candlestick</span>
        </div>
        <div className="flex items-center gap-1">
          {INTERVALS.map((iv) => (
            <button key={iv} onClick={() => setActiveInterval(iv)}
              className={`text-xs px-2 py-1 rounded transition-colors font-medium ${
                iv === activeInterval
                  ? 'bg-blue/20 text-blue'
                  : 'text-slate hover:text-white'
              }`}>
              {iv}
            </button>
          ))}
        </div>
      </div>

      {/* Chart container */}
      <div className="relative flex-1" style={{ height }}>
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-panel z-10">
            <div className="w-6 h-6 border-2 border-blue border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        <div ref={containerRef} style={{ width: '100%', height }} />
      </div>
    </div>
  )
}
