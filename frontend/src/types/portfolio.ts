export interface PortfolioStats {
  totalValue: number
  totalPnL: number
  totalPnLPct: number
  dayPnL: number
  winRate: number
  totalTrades: number
  winningTrades: number
  losingTrades: number
  avgWin: number
  avgLoss: number
  largestWin: number
  largestLoss: number
}

export interface AssetAllocation {
  symbol: string
  percentage: number
  value: number
}
