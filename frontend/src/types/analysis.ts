export type AnalysisMode = 'full' | 'financial' | 'valuation' | 'moat' | 'management'

export interface AnalysisRequest {
  mode: AnalysisMode
}

export interface AnalysisResult {
  ticker: string
  mode: AnalysisMode
  recommendation?: 'BUY' | 'HOLD' | 'SELL' | 'PASS'
  result: string
  timestamp?: string
}

export interface AnalysisHistory {
  ticker: string
  mode: AnalysisMode
  timestamp: string
  recommendation?: string
}
