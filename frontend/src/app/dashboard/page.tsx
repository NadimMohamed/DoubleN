'use client'
import React, { useState } from 'react'
import dynamic from 'next/dynamic'
import { useQuery } from '@tanstack/react-query'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { LiveTicker } from '@/components/dashboard/LiveTicker'
import { marketApi } from '@/lib/api'
import { formatPrice, formatPct, formatVolume, SYMBOL_DISPLAY } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, BarChart3, Activity } from 'lucide-react'
import type { TickerPrice } from '@/types'

const TradingChart = dynamic(
  () => import('@/components/charts/TradingChart').then((m) => ({ default: m.TradingChart })),
  { loading: () => <div className="card p-6 h-[420px] animate-pulse bg-panel-hover rounded" /> }
)

const DEFAULT_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'SOLUSDT']

const SymbolCard = React.memo(function SymbolCard({
  ticker,
  active,
  onClick,
}: {
  ticker: TickerPrice
  active: boolean
  onClick: () => void
}) {
  const up = ticker.price_change_pct >= 0
  const info = SYMBOL_DISPLAY[ticker.symbol] ?? { name: ticker.symbol, icon: '?' }

  return (
    <div onClick={onClick} className={cn(
      'card p-4 cursor-pointer transition-all duration-200',
      active ? 'border-blue/60 shadow-[0_0_20px_rgba(3,100,209,0.2)]' : 'hover:border-panel-border',
    )}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue/10 flex items-center justify-center text-blue font-bold text-sm">
            {info.icon}
          </div>
          <div>
            <div className="text-sm font-semibold text-white">{ticker.symbol.replace('USDT', '')}</div>
            <div className="text-xs text-slate">{info.name}</div>
          </div>
        </div>
        <div className={cn('flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded',
          up ? 'text-emerald bg-emerald/10' : 'text-danger bg-danger/10')}>
          {up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {formatPct(ticker.price_change_pct)}
        </div>
      </div>
      <div className="text-lg font-bold text-white tabular-nums">{formatPrice(ticker.price)}</div>
      <div className="text-xs text-slate mt-1">Vol: {formatVolume(ticker.quote_volume)}</div>
    </div>
  )
})

export default function DashboardPage() {
  const [activeSymbol, setActiveSymbol] = useState('BTCUSDT')

  const { data: tickers, isLoading, error } = useQuery({
    queryKey: ['tickers', DEFAULT_SYMBOLS],
    queryFn: () => marketApi.getTickers(DEFAULT_SYMBOLS),
    refetchInterval: 10_000,
    staleTime: 5_000,
  })

  const activeTicker = tickers?.find((t) => t.symbol === activeSymbol)

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-4 space-y-4">

            {/* Page header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-bold text-white">Dashboard</h1>
                <p className="text-sm text-slate mt-0.5">Live market data from Binance</p>
              </div>
              {activeTicker && (
                <LiveTicker
                  symbol={activeSymbol}
                  initialPrice={activeTicker.price}
                  initialChangePct={activeTicker.price_change_pct}
                  showDetails
                />
              )}
            </div>

            {/* Symbol cards */}
            {isLoading ? (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {DEFAULT_SYMBOLS.map((s) => (
                  <div key={s} className="card p-4 animate-pulse">
                    <div className="h-8 bg-panel-hover rounded mb-2" />
                    <div className="h-6 bg-panel-hover rounded w-2/3" />
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="card p-4 text-center text-danger text-sm">
                <p className="font-semibold mb-2">Failed to load market data</p>
                <p className="text-xs text-slate mb-3">
                  {error instanceof Error ? error.message : 'Check your connection or try refreshing'}
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="btn-primary text-xs px-3 py-1.5"
                >
                  Retry
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {tickers?.map((ticker) => (
                  <SymbolCard
                    key={ticker.symbol}
                    ticker={ticker}
                    active={activeSymbol === ticker.symbol}
                    onClick={() => setActiveSymbol(ticker.symbol)}
                  />
                ))}
              </div>
            )}

            {/* TradingView chart */}
            <TradingChart symbol={activeSymbol} interval="1h" height={420} />

            {/* Market stats row */}
            {activeTicker && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: '24h High', value: formatPrice(activeTicker.high_24h), icon: TrendingUp, color: 'text-emerald' },
                  { label: '24h Low',  value: formatPrice(activeTicker.low_24h),  icon: TrendingDown, color: 'text-danger' },
                  { label: 'Volume',   value: formatVolume(activeTicker.quote_volume), icon: BarChart3, color: 'text-blue' },
                  { label: 'Open',     value: formatPrice(activeTicker.open_price), icon: Activity, color: 'text-slate' },
                ].map(({ label, value, icon: Icon, color }) => (
                  <div key={label} className="card p-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-slate uppercase tracking-wider">{label}</span>
                      <Icon className={cn('w-3.5 h-3.5', color)} />
                    </div>
                    <div className="text-lg font-bold text-white tabular-nums">{value}</div>
                  </div>
                ))}
              </div>
            )}

          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
