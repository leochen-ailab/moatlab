import client from './client'
import type { ScreenRequest, StockScreenResult } from '../types/analysis'

// 筛选股票
export const screenStocks = (data: ScreenRequest) => {
  return client.post<any, StockScreenResult[]>('/api/screen', data)
}
