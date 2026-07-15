'use client'
import { Position } from '@/types/position'
import { useState } from 'react'
import { Modal } from '@/components/ui/Modal'
import { formatPrice, cn } from '@/lib/utils'

interface ClosePositionModalProps {
  position: Position
  onClose: (exitPrice: number) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export function ClosePositionModal({ position, onClose, onCancel, isLoading }: ClosePositionModalProps) {
  const [exitPrice, setExitPrice] = useState(position.current_price)

  const closePnl = position.side === 'long'
    ? (exitPrice - position.entry_price) * position.quantity
    : (position.entry_price - exitPrice) * position.quantity

  const closePnlPct = (closePnl / (position.entry_price * position.quantity)) * 100

  return (
    <Modal isOpen={true} onClose={onCancel} title="Close Position">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate uppercase tracking-wider block mb-2">Entry Price</label>
            <input
              type="number"
              value={position.entry_price}
              disabled
              className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-slate uppercase tracking-wider block mb-2">Exit Price</label>
            <input
              type="number"
              value={exitPrice}
              onChange={(e) => setExitPrice(Number(e.target.value))}
              className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm focus:border-blue"
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="card p-4 space-y-2">
          <div className="flex justify-between">
            <span className="text-slate">Quantity</span>
            <span className="text-white font-semibold">{position.quantity}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate">Profit/Loss</span>
            <span className={cn(closePnl >= 0 ? 'text-emerald' : 'text-danger', 'font-semibold')}>
              ${formatPrice(closePnl)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate">Return %</span>
            <span className={cn(closePnlPct >= 0 ? 'text-emerald' : 'text-danger', 'font-semibold')}>
              {closePnlPct.toFixed(2)}%
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 btn-secondary disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={() => onClose(exitPrice)}
            disabled={isLoading}
            className="flex-1 btn-primary disabled:opacity-50"
          >
            {isLoading ? 'Closing...' : 'Close Position'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
