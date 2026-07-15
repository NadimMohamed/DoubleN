'use client'
import { Position } from '@/types/position'
import { formatPrice, formatPct, cn } from '@/lib/utils'
import { X } from 'lucide-react'
import { useState } from 'react'
import { ClosePositionModal } from './ClosePositionModal'

interface PositionsTableProps {
  positions: Position[]
  onClose: (positionId: string, exitPrice: number) => Promise<void>
  isLoading?: boolean
}

export function PositionsTable({ positions, onClose, isLoading }: PositionsTableProps) {
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null)
  const [isClosing, setIsClosing] = useState(false)

  if (isLoading) {
    return <div className="text-slate">Loading positions...</div>
  }

  if (positions.length === 0) {
    return (
      <div className="card p-8 text-center text-slate">
        <p>No open positions</p>
      </div>
    )
  }

  return (
    <>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-panel-border">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate">Symbol</th>
              <th className="px-4 py-3 text-left font-semibold text-slate">Side</th>
              <th className="px-4 py-3 text-right font-semibold text-slate">Quantity</th>
              <th className="px-4 py-3 text-right font-semibold text-slate">Entry</th>
              <th className="px-4 py-3 text-right font-semibold text-slate">Current</th>
              <th className="px-4 py-3 text-right font-semibold text-slate">Leverage</th>
              <th className="px-4 py-3 text-right font-semibold text-slate">PnL</th>
              <th className="px-4 py-3 text-right font-semibold text-slate">PnL %</th>
              <th className="px-4 py-3 text-center font-semibold text-slate">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-panel-border">
            {positions.map((position) => (
              <tr key={position.id} className="hover:bg-panel-hover transition">
                <td className="px-4 py-3 font-bold text-white">{position.symbol}</td>
                <td className="px-4 py-3">
                  <span className={cn(
                    'px-2 py-1 rounded text-xs font-semibold',
                    position.side === 'long' ? 'bg-emerald/20 text-emerald' : 'bg-danger/20 text-danger'
                  )}>
                    {position.side.toUpperCase()}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-white">{position.quantity.toFixed(4)}</td>
                <td className="px-4 py-3 text-right text-slate">${formatPrice(position.entry_price)}</td>
                <td className="px-4 py-3 text-right text-white font-semibold">${formatPrice(position.current_price)}</td>
                <td className="px-4 py-3 text-right text-slate">{position.leverage}x</td>
                <td className={cn(
                  'px-4 py-3 text-right font-semibold',
                  position.unrealized_pnl >= 0 ? 'text-emerald' : 'text-danger'
                )}>
                  ${formatPrice(position.unrealized_pnl)}
                </td>
                <td className={cn(
                  'px-4 py-3 text-right font-semibold',
                  position.unrealized_pnl_pct >= 0 ? 'text-emerald' : 'text-danger'
                )}>
                  {formatPct(position.unrealized_pnl_pct)}
                </td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => setSelectedPosition(position)}
                    className="p-2 hover:bg-danger/20 rounded text-danger transition"
                    title="Close position"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedPosition && (
        <ClosePositionModal
          position={selectedPosition}
          onClose={async (exitPrice) => {
            setIsClosing(true)
            await onClose(selectedPosition.id, exitPrice)
            setSelectedPosition(null)
            setIsClosing(false)
          }}
          onCancel={() => setSelectedPosition(null)}
          isLoading={isClosing}
        />
      )}
    </>
  )
}
