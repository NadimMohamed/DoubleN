'use client'
import { Indicator } from '@/types/chart'

interface IndicatorToggleProps {
  enabled: Indicator[]
  onChange: (indicators: Indicator[]) => void
}

const INDICATORS: { id: Indicator; label: string; description: string }[] = [
  { id: 'sma', label: 'SMA 20', description: 'Simple Moving Average' },
  { id: 'ema', label: 'EMA 20', description: 'Exponential Moving Average' },
  { id: 'bollinger', label: 'Bollinger Bands', description: 'Volatility Indicator' },
  { id: 'rsi', label: 'RSI', description: 'Relative Strength Index' },
  { id: 'macd', label: 'MACD', description: 'Moving Average Convergence' },
]

export function IndicatorToggle({ enabled, onChange }: IndicatorToggleProps) {
  const toggle = (indicator: Indicator) => {
    const newIndicators = enabled.includes(indicator)
      ? enabled.filter(i => i !== indicator)
      : [...enabled, indicator]
    onChange(newIndicators)
  }

  return (
    <div className="card p-4 space-y-2">
      <h3 className="text-sm font-semibold text-white mb-3">Indicators</h3>
      {INDICATORS.map(({ id, label, description }) => (
        <label key={id} className="flex items-center gap-2 cursor-pointer hover:bg-panel-hover p-2 rounded">
          <input
            type="checkbox"
            checked={enabled.includes(id)}
            onChange={() => toggle(id)}
            className="w-4 h-4"
          />
          <div>
            <div className="text-xs font-medium text-white">{label}</div>
            <div className="text-xs text-slate">{description}</div>
          </div>
        </label>
      ))}
    </div>
  )
}
