import { ref } from 'vue'
import { defineStore } from 'pinia'
import { analyzeStock } from '../api/analysis'
import type { AnalysisMode, AnalysisResult, AnalysisHistory } from '../types/analysis'

export const useAnalysisStore = defineStore('analysis', () => {
  const currentResult = ref<AnalysisResult | null>(null)
  const history = ref<AnalysisHistory[]>([])
  const loading = ref(false)
  const progress = ref(0)

  const analyze = async (ticker: string, mode: AnalysisMode = 'full') => {
    loading.value = true
    progress.value = 0
    try {
      const result = await analyzeStock(ticker, mode)
      currentResult.value = result
      
      // 添加到历史记录
      history.value.unshift({
        ticker: result.ticker,
        mode: result.mode,
        timestamp: result.timestamp || new Date().toISOString(),
        recommendation: result.recommendation,
      })
      
      // 只保留最近 20 条
      if (history.value.length > 20) {
        history.value = history.value.slice(0, 20)
      }
      
      progress.value = 100
      return result
    } finally {
      loading.value = false
    }
  }

  const clearCurrent = () => {
    currentResult.value = null
    progress.value = 0
  }

  return {
    currentResult,
    history,
    loading,
    progress,
    analyze,
    clearCurrent,
  }
})
