export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w'
export type Indicator = 'sma' | 'ema' | 'bollinger' | 'rsi' | 'macd'

export interface Candle {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface ChartData {
  symbol: string
  timeframe: Timeframe
  candles: Candle[]
}
