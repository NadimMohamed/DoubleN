export interface Position {
  id: string
  symbol: string
  side: 'long' | 'short'
  quantity: number
  entry_price: number
  current_price: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
  leverage: number
  stop_loss?: number
  take_profit?: number
  status: 'open' | 'closed'
  opened_at: string
  closed_at?: string
}

export interface OpenPositionRequest {
  symbol: string
  side: 'long' | 'short'
  quantity: number
  entry_price: number
  leverage?: number
  stop_loss?: number
  take_profit?: number
}
