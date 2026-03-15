// 持仓相关类型定义
export interface Position {
  ticker: string
  company_name?: string
  shares: number
  avg_cost: number
  total_cost: number
  current_price?: number
  market_value?: number
  profit_loss?: number
  profit_loss_pct?: number
  first_buy_date: string
  last_trade_date: string
}

export interface Transaction {
  id?: number
  ticker: string
  action: 'buy' | 'sell'
  shares: number
  price: number
  trade_date: string
  notes?: string
}

export interface PortfolioSummary {
  total_cost: number
  total_market_value: number
  total_profit_loss: number
  total_return_pct: number
  position_count: number
  winners: number
  losers: number
}

export interface PortfolioPerformance {
  summary: PortfolioSummary
  positions: Position[]
}

// 交易请求
export interface TradeRequest {
  ticker: string
  shares: number
  price: number
  trade_date?: string
  notes?: string
}
