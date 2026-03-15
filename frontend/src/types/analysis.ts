// 分析相关类型定义
export type AnalysisMode = 'full' | 'financial' | 'valuation' | 'moat' | 'management'

export interface AnalyzeRequest {
  mode?: AnalysisMode
}

export interface AnalysisResult {
  ticker: string
  mode: AnalysisMode
  report: string
  timestamp: string
}

// 筛选相关类型定义
export interface ScreenRequest {
  roe_min?: number
  debt_equity_max?: number
  gross_margin_min?: number
  pe_min?: number
  pe_max?: number
  market_cap_min?: number
  market_cap_max?: number
  dividend_yield_min?: number
  sector?: string
}

export interface StockScreenResult {
  ticker: string
  company_name: string
  roe?: number
  debt_equity?: number
  gross_margin?: number
  pe?: number
  market_cap?: number
  dividend_yield?: number
  sector?: string
}
