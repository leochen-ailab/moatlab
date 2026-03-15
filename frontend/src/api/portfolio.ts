import { api } from "./client";
import type {
  PortfolioData,
  TradeRequest,
  TradeResult,
  TransactionHistory,
  Performance,
} from "../types/portfolio";

export function getPortfolio() {
  return api.get<PortfolioData>("/portfolio");
}

export function buy(req: TradeRequest) {
  return api.post<TradeResult>("/portfolio/buy", req);
}

export function sell(req: TradeRequest) {
  return api.post<TradeResult>("/portfolio/sell", req);
}

export function getPerformance() {
  return api.get<Performance>("/portfolio/performance");
}

export function getHistory(ticker?: string, limit = 50) {
  const params = new URLSearchParams();
  if (ticker) params.set("ticker", ticker);
  params.set("limit", String(limit));
  return api.get<TransactionHistory>(`/portfolio/history?${params}`);
}
