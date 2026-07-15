'use client'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const INDICATORS = [
  { id: 'sma20', label: 'SMA 20', color: 'text-blue' },
  { id: 'sma50', label: 'SMA 50', color: 'text-purple' },
  { id: 'rsi', label: 'RSI', color: 'text-emerald' },
  { id: 'macd', label: 'MACD', color: 'text-yellow-400' },
  { id: 'bollinger', label: 'Bollinger', color: 'text-orange' },
]

export function IndicatorOverlay({
  enabled,
  onToggle,
}: {
  enabled?: Set<string>
  onToggle?: (id: string) => void
} = {}) {
  const [internalEnabled, setInternalEnabled] = useState<Set<string>>(new Set(['sma20']))

  const activeEnabled = enabled ?? internalEnabled

  const toggle = (id: string) => {
    if (onToggle) {
      onToggle(id)
      return
    }
    const newSet = new Set(internalEnabled)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setInternalEnabled(newSet)
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-slate uppercase tracking-wider">Indicators</p>
      <div className="grid grid-cols-2 gap-2">
        {INDICATORS.map((ind) => (
          <label key={ind.id} className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={activeEnabled.has(ind.id)}
              onChange={() => toggle(ind.id)}
              className="w-4 h-4 rounded"
            />
            <span className={cn('text-xs font-semibold', ind.color)}>
              {ind.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  )
}
