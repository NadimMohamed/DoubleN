'use client'
import { useWebSocket } from '@/hooks/useWebSocket'
import { WebSocketMessage } from '@/lib/websocket'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { cn, formatPrice, formatPct } from '@/lib/utils'

export function LiveTicker({ symbol }: { symbol: string }) {
  const { isConnected, lastUpdate } = useWebSocket(symbol)

  if (!lastUpdate) {
    return <div className="text-slate">Connecting...</div>
  }

  const priceChange = lastUpdate.price_change_pct || 0
  const isPositive = priceChange >= 0

  return (
    <div className="flex items-center gap-4">
      <div className="flex-1">
        <div className="text-xs text-slate uppercase tracking-wider mb-1">Live Price</div>
        <div className="text-3xl font-bold text-white">
          ${formatPrice(lastUpdate.price)}
        </div>
      </div>

      <div className={cn(
        'flex items-center gap-1 px-3 py-2 rounded-lg',
        isPositive ? 'bg-emerald/20 text-emerald' : 'bg-danger/20 text-danger'
      )}>
        {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        <span className="text-sm font-semibold">{formatPct(priceChange)}</span>
      </div>

      <div className={cn(
        'w-2 h-2 rounded-full',
        isConnected ? 'bg-emerald' : 'bg-danger'
      )} title={isConnected ? 'Connected' : 'Disconnected'} />
    </div>
  )
}
