import { ref } from 'vue'
import { defineStore } from 'pinia'
import { screenStocks } from '../api/screener'
import type { ScreenCriteria, ScreenResponse } from '../types/screener'

export const useScreenerStore = defineStore('screener', () => {
  const result = ref<ScreenResponse | null>(null)
  const loading = ref(false)
  const criteria = ref<ScreenCriteria>({})

  const screen = async (newCriteria: ScreenCriteria) => {
    loading.value = true
    criteria.value = newCriteria
    try {
      const response = await screenStocks(newCriteria)
      result.value = response
      return response
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    criteria.value = {}
    result.value = null
  }

  return {
    result,
    loading,
    criteria,
    screen,
    reset,
  }
})
