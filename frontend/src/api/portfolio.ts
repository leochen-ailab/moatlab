import client from './client'
import type { Position, Transaction, PortfolioPerformance, TradeRequest } from '../types/portfolio'

// 获取所有持仓
export const getPortfolio = () => {
  return client.get<any, Position[]>('/api/portfolio')
}

// 获取持仓业绩
export const getPortfolioPerformance = () => {
  return client.get<any, PortfolioPerformance>('/api/portfolio/performance')
}

// 买入股票
export const buyStock = (data: TradeRequest) => {
  return client.post<any, { message: string }>('/api/portfolio/buy', data)
}

// 卖出股票
export const sellStock = (data: TradeRequest) => {
  return client.post<any, { message: string }>('/api/portfolio/sell', data)
}

// 获取交易历史
export const getTransactionHistory = (ticker?: string) => {
  return client.get<any, Transaction[]>('/api/portfolio/history', {
    params: { ticker }
  })
}
