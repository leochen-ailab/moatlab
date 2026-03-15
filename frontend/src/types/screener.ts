export interface ScreenRequest {
  roe_min?: number;
  debt_to_equity_max?: number;
  gross_margin_min?: number;
  pe_max?: number;
  sector?: string;
}

export interface ScreenResult {
  result: string; // markdown
}
