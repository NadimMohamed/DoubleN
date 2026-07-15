'use client'
import { PortfolioStats } from '@/types/portfolio'
import { formatPrice, formatPct } from '@/lib/utils'

interface TradingStatsProps {
  stats: PortfolioStats
}

export function TradingStats({ stats }: TradingStatsProps) {
  return (
    <div className="card p-6 space-y-4">
      <h3 className="text-lg font-bold text-white">Trading Statistics</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-xs text-slate uppercase tracking-wider">Total Trades</div>
          <div className="text-2xl font-bold text-white">{stats.totalTrades}</div>
        </div>
        <div>
          <div className="text-xs text-slate uppercase tracking-wider">Win Rate</div>
          <div className="text-2xl font-bold text-blue">{stats.winRate.toFixed(1)}%</div>
        </div>

        <div>
          <div className="text-xs text-slate uppercase tracking-wider">Wins / Losses</div>
          <div className="flex items-center gap-2">
            <span className="text-emerald font-bold">{stats.winningTrades}</span>
            <span className="text-slate">/</span>
            <span className="text-danger font-bold">{stats.losingTrades}</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-slate uppercase tracking-wider">Avg Win / Loss</div>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-emerald font-bold">${formatPrice(stats.avgWin)}</span>
            <span className="text-slate">/</span>
            <span className="text-danger font-bold">${formatPrice(Math.abs(stats.avgLoss))}</span>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-panel-border space-y-3">
        <div className="flex justify-between">
          <span className="text-slate">Largest Win</span>
          <span className="text-emerald font-bold">${formatPrice(stats.largestWin)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate">Largest Loss</span>
          <span className="text-danger font-bold">${formatPrice(stats.largestLoss)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate">Profit Factor</span>
          <span className="text-blue font-bold">
            {(stats.avgWin / Math.abs(stats.avgLoss)).toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  )
}
