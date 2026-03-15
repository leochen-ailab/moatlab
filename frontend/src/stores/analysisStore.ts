import { create } from "zustand";
import type { AnalysisMode, AnalysisResult } from "../types/analysis";
import * as analysisApi from "../api/analysis";

interface AnalysisStore {
  ticker: string;
  mode: AnalysisMode;
  result: AnalysisResult | null;
  loading: boolean;
  error: string | null;

  setTicker: (t: string) => void;
  setMode: (m: AnalysisMode) => void;
  analyze: () => Promise<void>;
  clear: () => void;
}

export const useAnalysisStore = create<AnalysisStore>((set, get) => ({
  ticker: "",
  mode: "full",
  result: null,
  loading: false,
  error: null,

  setTicker: (ticker) => set({ ticker: ticker.toUpperCase() }),
  setMode: (mode) => set({ mode }),

  analyze: async () => {
    const { ticker, mode } = get();
    if (!ticker) return;
    set({ loading: true, error: null, result: null });
    try {
      const result = await analysisApi.analyze(ticker, mode);
      set({ result, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  clear: () => set({ result: null, error: null }),
}));
