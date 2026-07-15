// ── Auth ──────────────────────────────────────────────────────────────────────
export interface User {
  id: string
  email: string
  username: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  expires_at: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
}

// ── Market ────────────────────────────────────────────────────────────────────
export interface TickerPrice {
  symbol: string
  price: number
  price_change: number
  price_change_pct: number
  high_24h: number
  low_24h: number
  volume: number
  quote_volume: number
  open_price: number
  last_updated: string
  // Where this data actually came from — Binance is frequently geo-blocked
  // (HTTP 451) from the hosting environment, so responses may fall back to
  // CoinGecko (real data, alternative source) or fully simulated mock data.
  data_source?: 'binance' | 'coingecko' | 'mock'
}

export interface KlineData {
  open_time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  close_time: number
  quote_volume: number
  num_trades: number
}

export interface OrderBookEntry {
  price: number
  quantity: number
}

export interface OrderBook {
  symbol: string
  bids: OrderBookEntry[]
  asks: OrderBookEntry[]
  last_update_id: number
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
export interface WsTickerMessage {
  type: 'ticker'
  symbol: string
  price: number
  open: number
  high: number
  low: number
  volume: number
  quote_volume: number
  timestamp: number
}

// ── Watchlist ─────────────────────────────────────────────────────────────────
export interface WatchlistItem {
  id: string
  symbol: string
  base_asset: string
  quote_asset: string
  added_at: string
  // Live prices (from backend enrichment)
  price: number | null
  price_change_24h: number | null
  price_change_pct_24h: number | null
  high_24h: number | null
  low_24h: number | null
  volume_24h: number | null
  quote_volume_24h: number | null
}

export interface AddToWatchlistRequest {
  symbol: string
}

// ── API error ─────────────────────────────────────────────────────────────────
export interface ApiError {
  detail: string | { msg: string; type: string }[]
}

// ── Auth (generic tokens) ───────────────────────────────────────────────────────
export interface AuthTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}

// ── Chart data (simplified, chart-library friendly) ─────────────────────────────
export interface Kline {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

// ── Trading Analysis ─────────────────────────────────────────────────────────────
export interface TrendAnalysis {
  direction: 'bullish' | 'bearish' | 'neutral'
  strength: number
}

export interface SupportResistance {
  support?: number
  resistance?: number
  pivot?: number
}

export interface Indicators {
  rsi?: number
}

export interface TradingSignal {
  signal: 'buy' | 'sell' | 'hold'
  confidence: number
  reasoning: string
}

export interface RiskManagement {
  entry_price: number
  stop_loss: number
  take_profit_2x: number
  take_profit_3x: number
  position_size?: number
  risk_amount?: number
}

export interface TradeAnalysis {
  symbol: string
  current_price: number
  trend: TrendAnalysis
  support_resistance: SupportResistance
  indicators: Indicators
  signal: TradingSignal
  risk_management: RiskManagement
  timestamp: string
}

// ── Portfolio ────────────────────────────────────────────────────────────────────
export interface Position {
  symbol: string
  quantity: number
  entry_price: number
  current_price: number
  pnl: number
  pnl_pct: number
}

// ── UI Types ─────────────────────────────────────────────────────────────────────
export type TimeFrame = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w'
export type ChartType = 'candlestick' | 'line' | 'area'
