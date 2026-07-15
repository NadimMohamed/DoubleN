'use client'
import { PortfolioStats } from '@/types/portfolio'
import { formatPrice, formatPct, cn } from '@/lib/utils'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface PortfolioStatsProps {
  stats: PortfolioStats
}

export function PortfolioStats({ stats }: PortfolioStatsProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="card p-4">
        <div className="text-xs text-slate uppercase tracking-wider mb-1">Portfolio Value</div>
        <div className="text-2xl font-bold text-white">${formatPrice(stats.totalValue)}</div>
      </div>

      <div className="card p-4">
        <div className="text-xs text-slate uppercase tracking-wider mb-1">Total P&L</div>
        <div className={cn(
          'text-2xl font-bold',
          stats.totalPnL >= 0 ? 'text-emerald' : 'text-danger'
        )}>
          ${formatPrice(stats.totalPnL)}
        </div>
        <div className={cn('text-xs', stats.totalPnLPct >= 0 ? 'text-emerald' : 'text-danger')}>
          {formatPct(stats.totalPnLPct)}
        </div>
      </div>

      <div className="card p-4">
        <div className="text-xs text-slate uppercase tracking-wider mb-1">Day P&L</div>
        <div className={cn(
          'text-2xl font-bold',
          stats.dayPnL >= 0 ? 'text-emerald' : 'text-danger'
        )}>
          ${formatPrice(stats.dayPnL)}
        </div>
      </div>

      <div className="card p-4">
        <div className="text-xs text-slate uppercase tracking-wider mb-1">Win Rate</div>
        <div className="text-2xl font-bold text-blue">{stats.winRate.toFixed(1)}%</div>
        <div className="text-xs text-slate">{stats.winningTrades}/{stats.totalTrades} trades</div>
      </div>
    </div>
  )
}
