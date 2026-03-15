import client from './client'
import type { AnalysisMode, AnalysisResult } from '../types/analysis'

export async function analyzeStock(ticker: string, mode: AnalysisMode = 'full'): Promise<AnalysisResult> {
  const response = await client.post(`/api/analyze/${ticker}`, { mode })
  return {
    ticker,
    mode,
    result: response.data.result || JSON.stringify(response.data, null, 2),
    timestamp: new Date().toISOString(),
  }
}
