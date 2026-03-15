export type AnalysisMode =
  | "full"
  | "financial"
  | "valuation"
  | "moat"
  | "management";

export interface AnalysisRequest {
  mode: AnalysisMode;
}

/** 全面分析返回各维度 key→markdown，单项分析返回 { result: markdown } */
export type AnalysisResult = Record<string, string>;
