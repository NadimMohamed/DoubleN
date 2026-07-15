'use client'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, AlertCircle, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import axios from 'axios'

interface MarketAnalysis {
  symbol: string
  current_price: number
  signal: {
    signal: 'buy' | 'sell' | 'neutral'
    confidence: number
    reasoning: string
  }
  trend: {
    direction: 'bullish' | 'bearish' | 'neutral'
    strength: number
  }
  support_resistance: {
    support?: number
    resistance?: number
  }
  indicators: {
    rsi?: number
    macd?: number
    macd_signal?: number
    ema_12?: number
    ema_26?: number
    atr?: number
  }
}

export function AIAnalysisCard({ symbol }: { symbol: string }) {
  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['analysis', symbol],
    queryFn: async () => {
      const res = await axios.get(`/api/v1/analysis/${symbol}`)
      return res.data as MarketAnalysis
    },
    refetchInterval: 30000,
    staleTime: 15000,
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="card p-6 space-y-4 animate-pulse">
        <div className="h-8 w-32 bg-panel-hover rounded" />
        <div className="grid grid-cols-3 gap-4">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-20 bg-panel-hover rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="card p-6 border border-danger/30 bg-danger/5">
        <p className="text-danger text-sm">Failed to load analysis</p>
      </div>
    )
  }

  const { signal, trend, support_resistance, indicators } = analysis
  const signalColor = signal.signal === 'buy' ? 'text-emerald bg-emerald/10' : 
                      signal.signal === 'sell' ? 'text-danger bg-danger/10' : 
                      'text-slate bg-slate/10'
  const trendColor = trend.direction === 'bullish' ? 'text-emerald' : 
                     trend.direction === 'bearish' ? 'text-danger' : 
                     'text-slate'

  return (
    <div className="card p-6 space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate uppercase tracking-wider mb-4">AI Analysis</h3>
        
        {/* Signal */}
        <div className={cn('p-4 rounded-lg border-2 mb-4', signalColor)}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-bold uppercase">{signal.signal}</p>
            <p className="text-xs font-semibold">{signal.confidence}% confidence</p>
          </div>
          <div className="w-full bg-black/20 rounded-full h-1.5 mb-3">
            <div 
              className={cn('h-full rounded-full transition-all', signal.signal === 'buy' ? 'bg-emerald' : signal.signal === 'sell' ? 'bg-danger' : 'bg-slate')}
              style={{ width: `${signal.confidence}%` }}
            />
          </div>
          <p className="text-xs text-current/80">{signal.reasoning}</p>
        </div>

        {/* Trend & Indicators Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Trend */}
          <div className="bg-panel-hover p-3 rounded-lg">
            <p className="text-xs text-slate mb-1">Trend</p>
            <p className={cn('text-lg font-bold capitalize', trendColor)}>
              {trend.direction}
            </p>
            <p className="text-xs text-slate mt-1">Strength: {trend.strength}%</p>
          </div>

          {/* RSI */}
          {indicators.rsi !== undefined && (
            <div className="bg-panel-hover p-3 rounded-lg">
              <p className="text-xs text-slate mb-1">RSI</p>
              <p className={cn('text-lg font-bold', 
                indicators.rsi < 30 ? 'text-emerald' : 
                indicators.rsi > 70 ? 'text-danger' : 'text-slate'
              )}>
                {indicators.rsi.toFixed(1)}
              </p>
              <p className="text-xs text-slate mt-1">
                {indicators.rsi < 30 ? 'Oversold' : indicators.rsi > 70 ? 'Overbought' : 'Neutral'}
              </p>
            </div>
          )}

          {/* Support */}
          {support_resistance.support && (
            <div className="bg-panel-hover p-3 rounded-lg">
              <p className="text-xs text-slate mb-1">Support</p>
              <p className="text-lg font-bold text-emerald">${support_resistance.support.toFixed(2)}</p>
            </div>
          )}

          {/* Resistance */}
          {support_resistance.resistance && (
            <div className="bg-panel-hover p-3 rounded-lg">
              <p className="text-xs text-slate mb-1">Resistance</p>
              <p className="text-lg font-bold text-danger">${support_resistance.resistance.toFixed(2)}</p>
            </div>
          )}

          {/* MACD */}
          {indicators.macd !== undefined && (
            <div className="bg-panel-hover p-3 rounded-lg">
              <p className="text-xs text-slate mb-1">MACD</p>
              <p className={cn('text-lg font-bold', indicators.macd > (indicators.macd_signal || 0) ? 'text-emerald' : 'text-danger')}>
                {indicators.macd.toFixed(4)}
              </p>
            </div>
          )}

          {/* EMA 12/26 */}
          {indicators.ema_12 && (
            <div className="bg-panel-hover p-3 rounded-lg">
              <p className="text-xs text-slate mb-1">EMA 12/26</p>
              <p className={cn('text-lg font-bold', indicators.ema_12 > (indicators.ema_26 || 0) ? 'text-emerald' : 'text-danger')}>
                {indicators.ema_12 > (indicators.ema_26 || 0) ? '↑' : '↓'} {(indicators.ema_12 || 0).toFixed(0)}
              </p>
            </div>
          )}

          {/* ATR */}
          {indicators.atr !== undefined && (
            <div className="bg-panel-hover p-3 rounded-lg">
              <p className="text-xs text-slate mb-1">ATR</p>
              <p className="text-lg font-bold text-blue">{indicators.atr.toFixed(2)}</p>
              <p className="text-xs text-slate mt-1">Volatility</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
