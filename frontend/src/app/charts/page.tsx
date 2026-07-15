'use client'
import { useState } from 'react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { AdvancedChart } from '@/components/charting/AdvancedChart'
import { IndicatorToggle } from '@/components/charting/IndicatorToggle'
import { Timeframe, Indicator } from '@/types/chart'
import { TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export default function ChartsPage() {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [timeframe, setTimeframe] = useState<Timeframe>('1h')
  const [indicators, setIndicators] = useState<Indicator[]>(['sma'])

  const { data: candles = [] } = useQuery({
    queryKey: ['klines', symbol, timeframe],
    queryFn: async () => {
      const res = await api.get(`/market/klines/${symbol}?interval=${timeframe}&limit=100`)
      return res.data
    },
    refetchInterval: timeframe === '1m' ? 30000 : 60000,
  })

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-6 h-6" />
                Advanced Charts
              </h1>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-3">
                <AdvancedChart
                  symbol={symbol}
                  candles={candles}
                  timeframe={timeframe}
                  onTimeframeChange={setTimeframe}
                  indicators={indicators}
                />
              </div>

              <div className="space-y-4">
                <div className="card p-4">
                  <label className="text-xs text-slate uppercase tracking-wider block mb-2">Symbol</label>
                  <select
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
                  >
                    <option>BTCUSDT</option>
                    <option>ETHUSDT</option>
                    <option>BNBUSDT</option>
                    <option>ADAUSDT</option>
                  </select>
                </div>

                <IndicatorToggle enabled={indicators} onChange={setIndicators} />
              </div>
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
