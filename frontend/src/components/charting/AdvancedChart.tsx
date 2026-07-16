'use client'
import { LineChart, Line, BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, ComposedChart } from 'recharts'
import { useState } from 'react'
import { Candle, Timeframe, Indicator } from '@/types/chart'
import { formatPrice } from '@/lib/utils'

interface AdvancedChartProps {
  symbol: string
  candles: Candle[]
  timeframe: Timeframe
  onTimeframeChange: (tf: Timeframe) => void
  indicators?: Indicator[]
}

const TIMEFRAMES: Timeframe[] = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']

export function AdvancedChart({ symbol, candles, timeframe, onTimeframeChange, indicators = [] }: AdvancedChartProps) {
  const data = candles.map(c => ({
    timestamp: new Date(c.timestamp).toLocaleTimeString(),
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
    volume: c.volume,
  }))

  return (
    <div className="card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white">{symbol}</h3>
        <div className="flex gap-2">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange(tf)}
              className={`px-3 py-1 rounded text-xs font-semibold transition ${
                tf === timeframe
                  ? 'bg-blue text-white'
                  : 'bg-panel-hover text-slate hover:bg-panel-border'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={data}>
          <XAxis dataKey="timestamp" stroke="#6b7280" tick={{ fontSize: 12 }} />
          <YAxis stroke="#6b7280" domain={['dataMin', 'dataMax']} tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1a1f3a', border: '1px solid #4b5563' }}
            labelStyle={{ color: '#ffffff' }}
            formatter={(value: any) => formatPrice(value)}
          />
          <Legend />
          <Bar dataKey="volume" fill="#6b7280" opacity={0.3} />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#3b82f6"
            dot={false}
            name="Price"
          />
          {indicators.includes('sma') && (
            <Line
              type="monotone"
              dataKey="sma20"
              stroke="#fbbf24"
              dot={false}
              name="SMA 20"
            />
          )}
          {indicators.includes('bollinger') && (
            <>
              <Line type="monotone" dataKey="bbUpper" stroke="#ef4444" dot={false} strokeDasharray="5 5" />
              <Line type="monotone" dataKey="bbLower" stroke="#ef4444" dot={false} strokeDasharray="5 5" />
            </>
          )}
        </ComposedChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-4 gap-4 text-xs">
        <div className="card p-2 bg-panel-hover">
          <div className="text-slate">Open</div>
          <div className="text-white font-bold">${formatPrice(candles[0]?.open || 0)}</div>
        </div>
        <div className="card p-2 bg-panel-hover">
          <div className="text-slate">High</div>
          <div className="text-emerald font-bold">${formatPrice(Math.max(...candles.map(c => c.high)))}</div>
        </div>
        <div className="card p-2 bg-panel-hover">
          <div className="text-slate">Low</div>
          <div className="text-danger font-bold">${formatPrice(Math.min(...candles.map(c => c.low)))}</div>
        </div>
        <div className="card p-2 bg-panel-hover">
          <div className="text-slate">Close</div>
          <div className="text-white font-bold">${formatPrice(candles[candles.length - 1]?.close || 0)}</div>
        </div>
      </div>
    </div>
  )
}
