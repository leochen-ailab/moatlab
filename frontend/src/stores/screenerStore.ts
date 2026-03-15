import { create } from "zustand";
import type { ScreenRequest, ScreenResult } from "../types/screener";
import * as screenerApi from "../api/screener";

interface ScreenerStore {
  criteria: ScreenRequest;
  result: ScreenResult | null;
  loading: boolean;
  error: string | null;

  setCriteria: (c: Partial<ScreenRequest>) => void;
  screen: () => Promise<void>;
  clear: () => void;
}

export const useScreenerStore = create<ScreenerStore>((set, get) => ({
  criteria: {},
  result: null,
  loading: false,
  error: null,

  setCriteria: (c) =>
    set((s) => ({ criteria: { ...s.criteria, ...c } })),

  screen: async () => {
    const { criteria } = get();
    set({ loading: true, error: null, result: null });
    try {
      const result = await screenerApi.screen(criteria);
      set({ result, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  clear: () => set({ criteria: {}, result: null, error: null }),
}));
