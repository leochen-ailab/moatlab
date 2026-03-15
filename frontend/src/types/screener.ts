export interface ScreenCriteria {
  roe_min?: number
  debt_to_equity_max?: number
  gross_margin_min?: number
  pe_max?: number
  sector?: string
}

export interface ScreenResult {
  ticker: string
  company_name?: string
  roe?: number
  debt_to_equity?: number
  gross_margin?: number
  pe?: number
  market_cap?: number
  dividend_yield?: number
  sector?: string
}

export interface ScreenResponse {
  result: string
  count?: number
  stocks?: ScreenResult[]
}
