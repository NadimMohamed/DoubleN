'use client'
import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, HelpCircle } from 'lucide-react'
import { formatPrice, formatPct } from '@/lib/utils'
import { cn } from '@/lib/utils'

// Mock trading data - replace with actual API calls
async function getTradeAnalysis(symbol: string) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/trading/analysis/${symbol}?interval=1h&lookback=100&account_balance=10000`
  )
  if (!response.ok) throw new Error('Failed to fetch analysis')
  return response.json()
}

export default function TradingPage() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const [accountBalance, setAccountBalance] = useState(10000)

  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['tradeAnalysis', selectedSymbol],
    queryFn: () => getTradeAnalysis(selectedSymbol),
    refetchInterval: 30000,
  })

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy':
        return 'text-emerald bg-emerald/10 border-emerald/30'
      case 'sell':
        return 'text-danger bg-danger/10 border-danger/30'
      default:
        return 'text-slate bg-slate/10 border-slate/30'
    }
  }

  const getTrendIcon = (direction: string) => {
    return direction === 'bullish' ? (
      <TrendingUp className="w-4 h-4 text-emerald" />
    ) : direction === 'bearish' ? (
      <TrendingDown className="w-4 h-4 text-danger" />
    ) : (
      <HelpCircle className="w-4 h-4 text-slate" />
    )
  }

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-white">Trading Analysis</h1>
              <p className="text-slate text-sm mt-1">AI-powered signals and risk management</p>
            </div>

            {/* Symbol & Balance Controls */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="card p-4">
                <label className="text-xs text-slate uppercase tracking-wider block mb-2">Symbol</label>
                <select
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm focus:border-blue focus:outline-none"
                >
                  <option>BTCUSDT</option>
                  <option>ETHUSDT</option>
                  <option>LTCUSDT</option>
                  <option>SOLUSDT</option>
                </select>
              </div>
              <div className="card p-4">
                <label className="text-xs text-slate uppercase tracking-wider block mb-2">Account Balance</label>
                <input
                  type="number"
                  value={accountBalance}
                  onChange={(e) => setAccountBalance(Number(e.target.value))}
                  className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm focus:border-blue focus:outline-none"
                />
              </div>
            </div>

            {isLoading ? (
              <div className="card p-8 text-center">
                <div className="animate-spin h-8 w-8 border-4 border-blue border-t-transparent rounded-full mx-auto mb-4" />
                <p className="text-slate text-sm">Analyzing {selectedSymbol}...</p>
              </div>
            ) : error ? (
              <div className="card p-6 border border-danger/30 bg-danger/10">
                <p className="text-danger font-semibold">Failed to load analysis</p>
                <p className="text-slate text-sm mt-1">{error instanceof Error ? error.message : 'Try again later'}</p>
              </div>
            ) : analysis ? (
              <>
                {/* Signal Card */}
                <div className={cn('card p-6 border-2', getSignalColor(analysis.signal.signal))}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-xs text-slate uppercase tracking-wider mb-1">Trading Signal</p>
                      <p className="text-3xl font-bold uppercase">{analysis.signal.signal}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate uppercase tracking-wider mb-1">Confidence</p>
                      <p className="text-2xl font-bold">{analysis.signal.confidence.toFixed(1)}%</p>
                    </div>
                  </div>
                  <p className="text-sm text-slate">{analysis.signal.reasoning}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Trend */}
                  <div className="card p-4">
                    <div className="flex items-center gap-2 mb-3">
                      {getTrendIcon(analysis.trend.direction)}
                      <span className="text-xs text-slate uppercase tracking-wider">Trend</span>
                    </div>
                    <p className="text-xl font-bold text-white capitalize">{analysis.trend.direction}</p>
                    <p className="text-xs text-slate mt-2">Strength: {analysis.trend.strength.toFixed(1)}/100</p>
                  </div>

                  {/* Support/Resistance */}
                  <div className="card p-4">
                    <p className="text-xs text-slate uppercase tracking-wider mb-3">Support/Resistance</p>
                    {analysis.support_resistance.support && (
                      <div className="mb-2">
                        <p className="text-xs text-slate">Support</p>
                        <p className="text-lg font-bold text-emerald">${analysis.support_resistance.support.toFixed(2)}</p>
                      </div>
                    )}
                    {analysis.support_resistance.resistance && (
                      <div>
                        <p className="text-xs text-slate">Resistance</p>
                        <p className="text-lg font-bold text-danger">${analysis.support_resistance.resistance.toFixed(2)}</p>
                      </div>
                    )}
                  </div>

                  {/* Indicators */}
                  <div className="card p-4">
                    <p className="text-xs text-slate uppercase tracking-wider mb-3">Indicators</p>
                    {analysis.indicators.rsi && (
                      <div>
                        <p className="text-xs text-slate">RSI (14)</p>
                        <p className={cn(
                          'text-lg font-bold',
                          analysis.indicators.rsi > 70 ? 'text-danger' :
                          analysis.indicators.rsi < 30 ? 'text-emerald' : 'text-blue'
                        )}>
                          {analysis.indicators.rsi.toFixed(1)}
                        </p>
                        <p className="text-xs text-slate mt-1">
                          {analysis.indicators.rsi > 70 ? 'Overbought' :
                           analysis.indicators.rsi < 30 ? 'Oversold' : 'Neutral'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Risk Management */}
                <div className="card p-6">
                  <h3 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Risk Management</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate uppercase tracking-wider mb-2">Entry Price</p>
                      <p className="text-2xl font-bold text-white">${analysis.risk_management.entry_price.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate uppercase tracking-wider mb-2">Current Price</p>
                      <p className="text-2xl font-bold text-white">${analysis.current_price.toFixed(2)}</p>
                    </div>
                    <div className="border-t border-panel-border pt-4">
                      <p className="text-xs text-slate uppercase tracking-wider mb-2 text-danger">Stop Loss</p>
                      <p className="text-lg font-bold text-danger">${analysis.risk_management.stop_loss.toFixed(2)}</p>
                    </div>
                    <div className="border-t border-panel-border pt-4">
                      <p className="text-xs text-slate uppercase tracking-wider mb-2 text-emerald">Take Profit (2x)</p>
                      <p className="text-lg font-bold text-emerald">${analysis.risk_management.take_profit_2x.toFixed(2)}</p>
                    </div>
                  </div>
                  {analysis.risk_management.position_size && (
                    <div className="mt-4 pt-4 border-t border-panel-border">
                      <p className="text-xs text-slate uppercase tracking-wider mb-2">Position Size</p>
                      <p className="text-lg font-bold text-blue">{analysis.risk_management.position_size.toFixed(4)} {selectedSymbol.replace('USDT', '')}</p>
                      <p className="text-xs text-slate mt-1">Risk Amount: ${analysis.risk_management.risk_amount?.toFixed(2)}</p>
                    </div>
                  )}
                </div>

                {/* Disclaimer */}
                <div className="card p-4 border border-slate/30 bg-slate/5 flex gap-3">
                  <AlertTriangle className="w-5 h-5 text-slate flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-slate">
                    <p className="font-semibold mb-1">Trading Disclaimer</p>
                    <p>This analysis is for informational purposes only. All signals are probability-based and not guaranteed. Past performance does not indicate future results. Always conduct your own research and consult a financial advisor before trading.</p>
                  </div>
                </div>
              </>
            ) : null}
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
