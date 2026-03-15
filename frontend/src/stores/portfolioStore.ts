import { create } from "zustand";
import type {
  PortfolioData,
  TradeRequest,
  Performance,
  TransactionHistory,
} from "../types/portfolio";
import * as portfolioApi from "../api/portfolio";

interface PortfolioStore {
  data: PortfolioData | null;
  performance: Performance | null;
  history: TransactionHistory | null;
  loading: boolean;
  error: string | null;

  fetchPortfolio: () => Promise<void>;
  fetchPerformance: () => Promise<void>;
  fetchHistory: (ticker?: string, limit?: number) => Promise<void>;
  buy: (req: TradeRequest) => Promise<void>;
  sell: (req: TradeRequest) => Promise<void>;
}

export const usePortfolioStore = create<PortfolioStore>((set, get) => ({
  data: null,
  performance: null,
  history: null,
  loading: false,
  error: null,

  fetchPortfolio: async () => {
    set({ loading: true, error: null });
    try {
      const data = await portfolioApi.getPortfolio();
      set({ data, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  fetchPerformance: async () => {
    try {
      const performance = await portfolioApi.getPerformance();
      set({ performance });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  fetchHistory: async (ticker?: string, limit?: number) => {
    set({ loading: true, error: null });
    try {
      const history = await portfolioApi.getHistory(ticker, limit);
      set({ history, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  buy: async (req: TradeRequest) => {
    await portfolioApi.buy(req);
    await get().fetchPortfolio();
  },

  sell: async (req: TradeRequest) => {
    await portfolioApi.sell(req);
    await get().fetchPortfolio();
  },
}));
