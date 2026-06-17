import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number | null | undefined): string {
  if (price == null) return '—'
  if (price >= 1000) return '$' + price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  if (price >= 1) return '$' + price.toFixed(4)
  return '$' + price.toFixed(6)
}

export function formatPct(pct: number | null | undefined): string {
  if (pct == null) return '—'
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

export function formatVolume(vol: number | null | undefined): string {
  if (vol == null) return '—'
  if (vol >= 1_000_000_000) return `$${(vol / 1_000_000_000).toFixed(2)}B`
  if (vol >= 1_000_000) return `$${(vol / 1_000_000).toFixed(2)}M`
  if (vol >= 1_000) return `$${(vol / 1_000).toFixed(2)}K`
  return `$${vol.toFixed(2)}`
}

export function formatChange(change: number | null | undefined): string {
  if (change == null) return '—'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${formatPrice(change)}`
}

export const SUPPORTED_SYMBOLS = [
  'BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'SOLUSDT',
  'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT',
  'MATICUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT',
]

export const SYMBOL_DISPLAY: Record<string, { name: string; icon: string }> = {
  BTCUSDT:   { name: 'Bitcoin',        icon: '₿' },
  ETHUSDT:   { name: 'Ethereum',       icon: 'Ξ' },
  LTCUSDT:   { name: 'Litecoin',       icon: 'Ł' },
  SOLUSDT:   { name: 'Solana',         icon: '◎' },
  BNBUSDT:   { name: 'BNB',            icon: 'B' },
  XRPUSDT:   { name: 'XRP',            icon: 'X' },
  ADAUSDT:   { name: 'Cardano',        icon: '₳' },
  DOGEUSDT:  { name: 'Dogecoin',       icon: 'Ð' },
  MATICUSDT: { name: 'Polygon',        icon: 'M' },
  DOTUSDT:   { name: 'Polkadot',       icon: '●' },
  AVAXUSDT:  { name: 'Avalanche',      icon: 'A' },
  LINKUSDT:  { name: 'Chainlink',      icon: '⬡' },
}
