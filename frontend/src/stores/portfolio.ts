import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Position, Transaction, PortfolioPerformance } from '../types/portfolio'
import * as portfolioApi from '../api/portfolio'

export const usePortfolioStore = defineStore('portfolio', () => {
  // 状态
  const positions = ref<Position[]>([])
  const transactions = ref<Transaction[]>([])
  const performance = ref<PortfolioPerformance | null>(null)
  const loading = ref(false)

  // 获取持仓列表
  const fetchPortfolio = async () => {
    loading.value = true
    try {
      positions.value = await portfolioApi.getPortfolio()
    } finally {
      loading.value = false
    }
  }

  // 获取持仓业绩
  const fetchPerformance = async () => {
    loading.value = true
    try {
      performance.value = await portfolioApi.getPortfolioPerformance()
      positions.value = performance.value.positions
    } finally {
      loading.value = false
    }
  }

  // 获取交易历史
  const fetchTransactions = async (ticker?: string) => {
    loading.value = true
    try {
      transactions.value = await portfolioApi.getTransactionHistory(ticker)
    } finally {
      loading.value = false
    }
  }

  // 买入股票
  const buyStock = async (data: {
    ticker: string
    shares: number
    price: number
    trade_date?: string
    notes?: string
  }) => {
    await portfolioApi.buyStock(data)
    await fetchPerformance()
  }

  // 卖出股票
  const sellStock = async (data: {
    ticker: string
    shares: number
    price: number
    trade_date?: string
    notes?: string
  }) => {
    await portfolioApi.sellStock(data)
    await fetchPerformance()
  }

  return {
    positions,
    transactions,
    performance,
    loading,
    fetchPortfolio,
    fetchPerformance,
    fetchTransactions,
    buyStock,
    sellStock,
  }
})
