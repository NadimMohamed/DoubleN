'use client'
import React, { useEffect, useRef, useState, useMemo } from 'react'
import { useTickerStream } from '@/hooks/useTickerStream'
import { formatPrice, formatPct } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface LiveTickerProps {
  symbol: string
  initialPrice?: number | null
  initialChangePct?: number | null
  showDetails?: boolean
}

function LiveTickerComponent({
  symbol,
  initialPrice,
  initialChangePct,
  showDetails = false,
}: LiveTickerProps) {
  const { price, high, low, volume, isConnected } = useTickerStream({ symbol })
  const [flash, setFlash] = useState<'up' | 'down' | null>(null)
  const prevPrice = useRef<number | null>(null)

  const displayPrice = price ?? initialPrice
  const changePct = initialChangePct
  const isPositive = useMemo(() => (changePct ?? 0) >= 0, [changePct])

  // Flash animation on price change
  useEffect(() => {
    if (price !== null && prevPrice.current !== null) {
      setFlash(price > prevPrice.current ? 'up' : 'down')
      const t = setTimeout(() => setFlash(null), 600)
      return () => clearTimeout(t)
    }
    prevPrice.current = price
  }, [price])

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        {/* Live indicator */}
        <div
          className={cn(
            'w-1.5 h-1.5 rounded-full flex-shrink-0',
            isConnected ? 'bg-emerald animate-pulse' : 'bg-slate'
          )}
        />

        {/* Price */}
        <span
          className={cn(
            'text-2xl font-bold tabular-nums transition-colors duration-300',
            flash === 'up' && 'text-emerald',
            flash === 'down' && 'text-danger',
            !flash && 'text-white'
          )}
        >
          {formatPrice(displayPrice)}
        </span>

        {/* 24h change */}
        {changePct !== null && changePct !== undefined && (
          <div
            className={cn(
              'flex items-center gap-0.5 text-sm font-medium',
              isPositive ? 'text-emerald' : 'text-danger'
            )}
          >
            {isPositive ? (
              <TrendingUp className="w-3.5 h-3.5" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5" />
            )}
            {formatPct(changePct)}
          </div>
        )}
      </div>

      {showDetails && (
        <div className="flex items-center gap-4 text-xs text-slate">
          {high && <span>H: <span className="text-emerald">{formatPrice(high)}</span></span>}
          {low && <span>L: <span className="text-danger">{formatPrice(low)}</span></span>}
          {volume && (
            <span>
              Vol: <span className="text-white">{volume.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export const LiveTicker = React.memo(LiveTickerComponent)
