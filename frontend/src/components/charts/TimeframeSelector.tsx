'use client'
import { cn } from '@/lib/utils'

const TIMEFRAMES = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' },
  { label: '1w', value: '1w' },
]

export function TimeframeSelector({ 
  value, 
  onChange 
}: { 
  value: string
  onChange: (tf: string) => void 
}) {
  return (
    <div className="flex gap-1 p-2 bg-panel-hover rounded-lg">
      {TIMEFRAMES.map((tf) => (
        <button
          key={tf.value}
          onClick={() => onChange(tf.value)}
          className={cn(
            'px-2 py-1 rounded text-xs font-semibold transition-colors',
            value === tf.value
              ? 'bg-blue text-white'
              : 'text-slate hover:text-white hover:bg-panel-border'
          )}
        >
          {tf.label}
        </button>
      ))}
    </div>
  )
}
