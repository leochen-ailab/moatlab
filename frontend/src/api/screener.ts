import { api } from "./client";
import type { ScreenRequest, ScreenResult } from "../types/screener";

export function screen(criteria?: ScreenRequest) {
  return api.post<ScreenResult>("/screen", criteria);
}
