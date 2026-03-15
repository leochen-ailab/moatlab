import { api } from "./client";
import type { AnalysisMode, AnalysisResult } from "../types/analysis";

export function analyze(ticker: string, mode: AnalysisMode = "full") {
  return api.post<AnalysisResult>(`/analyze/${ticker}`, { mode });
}
