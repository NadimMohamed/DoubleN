'use client'
import { useState } from 'react'
import { OpenPositionRequest } from '@/types/position'

interface OpenPositionFormProps {
  onSubmit: (data: OpenPositionRequest) => Promise<void>
  isLoading?: boolean
  symbols?: string[]
}

export function OpenPositionForm({ onSubmit, isLoading, symbols = [] }: OpenPositionFormProps) {
  const [formData, setFormData] = useState<OpenPositionRequest>({
    symbol: symbols[0] || 'BTCUSDT',
    side: 'long',
    quantity: 1,
    entry_price: 0,
    leverage: 1,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="card p-6 space-y-4">
      <h3 className="text-lg font-semibold text-white">Open Position</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Symbol</label>
          <select
            value={formData.symbol}
            onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          >
            {symbols.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Side</label>
          <select
            value={formData.side}
            onChange={(e) => setFormData({ ...formData, side: e.target.value as 'long' | 'short' })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          >
            <option value="long">Long</option>
            <option value="short">Short</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Quantity</label>
          <input
            type="number"
            step="0.0001"
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: Number(e.target.value) })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Entry Price</label>
          <input
            type="number"
            step="0.01"
            value={formData.entry_price}
            onChange={(e) => setFormData({ ...formData, entry_price: Number(e.target.value) })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Leverage</label>
          <input
            type="number"
            step="0.1"
            min="1"
            max="10"
            value={formData.leverage}
            onChange={(e) => setFormData({ ...formData, leverage: Number(e.target.value) })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Stop Loss (optional)</label>
          <input
            type="number"
            step="0.01"
            value={formData.stop_loss || ''}
            onChange={(e) => setFormData({ ...formData, stop_loss: e.target.value ? Number(e.target.value) : undefined })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-slate uppercase tracking-wider block mb-2">Take Profit (optional)</label>
          <input
            type="number"
            step="0.01"
            value={formData.take_profit || ''}
            onChange={(e) => setFormData({ ...formData, take_profit: e.target.value ? Number(e.target.value) : undefined })}
            className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full btn-primary disabled:opacity-50"
      >
        {isLoading ? 'Opening...' : 'Open Position'}
      </button>
    </form>
  )
}
