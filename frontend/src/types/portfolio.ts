export interface Position {
  ticker: string;
  shares: number;
  avg_cost: number;
  total_cost: number;
  current_price: number;
  market_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface PortfolioData {
  positions: Position[];
  total_cost: number;
  total_market_value: number;
  total_return: number;
  total_return_pct: number;
}

export interface TradeRequest {
  ticker: string;
  shares: number;
  price: number;
  trade_date?: string;
  notes?: string;
}

export interface TradeResult {
  status: string;
  message?: string;
  position?: Position;
}

export interface Transaction {
  date: string;
  action: "buy" | "sell";
  ticker: string;
  shares: number;
  price: number;
  notes?: string;
}

export interface TransactionHistory {
  transactions: Transaction[];
}

export interface Performance {
  winners: Position[];
  losers: Position[];
}
