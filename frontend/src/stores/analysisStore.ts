import { create } from "zustand";
import type { AnalysisMode, AnalysisResult } from "../types/analysis";
import * as analysisApi from "../api/analysis";

const HISTORY_KEY = "moatlab-analysis-history";
const MAX_HISTORY = 10;

export interface AnalysisHistoryEntry {
  ticker: string;
  mode: AnalysisMode;
  result: AnalysisResult;
  timestamp: number;
}

function loadHistory(): AnalysisHistoryEntry[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(history: AnalysisHistoryEntry[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)));
}

interface AnalysisStore {
  ticker: string;
  mode: AnalysisMode;
  result: AnalysisResult | null;
  loading: boolean;
  error: string | null;
  history: AnalysisHistoryEntry[];

  setTicker: (t: string) => void;
  setMode: (m: AnalysisMode) => void;
  analyze: () => Promise<void>;
  clear: () => void;
  loadFromHistory: (entry: AnalysisHistoryEntry) => void;
  clearHistory: () => void;
}

export const useAnalysisStore = create<AnalysisStore>((set, get) => ({
  ticker: "",
  mode: "full",
  result: null,
  loading: false,
  error: null,
  history: loadHistory(),

  setTicker: (ticker) => set({ ticker: ticker.toUpperCase() }),
  setMode: (mode) => set({ mode }),

  analyze: async () => {
    const { ticker, mode } = get();
    if (!ticker) return;
    set({ loading: true, error: null, result: null });
    try {
      const result = await analysisApi.analyze(ticker, mode);
      const entry: AnalysisHistoryEntry = {
        ticker,
        mode,
        result,
        timestamp: Date.now(),
      };
      const history = [entry, ...get().history.filter(
        (h) => !(h.ticker === ticker && h.mode === mode),
      )].slice(0, MAX_HISTORY);
      saveHistory(history);
      set({ result, loading: false, history });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  clear: () => set({ result: null, error: null }),

  loadFromHistory: (entry) =>
    set({
      ticker: entry.ticker,
      mode: entry.mode,
      result: entry.result,
      error: null,
    }),

  clearHistory: () => {
    localStorage.removeItem(HISTORY_KEY);
    set({ history: [] });
  },
}));
