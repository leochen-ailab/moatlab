import client from './client'
import type { AnalyzeRequest, AnalysisResult } from '../types/analysis'

// 分析股票
export const analyzeStock = (ticker: string, data?: AnalyzeRequest) => {
  return client.post<any, AnalysisResult>(`/api/analyze/${ticker}`, data || {})
}
