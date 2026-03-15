<template>
  <div class="portfolio-page">
    <el-row :gutter="24">
      <el-col :span="24">
        <SummaryCard
          :summary="portfolioStore.performance?.summary || null"
          :loading="portfolioStore.loading"
          @refresh="handleRefresh"
        />
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="16">
        <PositionTable
          :positions="portfolioStore.positions"
          :loading="portfolioStore.loading"
          @add="handleShowBuyDialog"
          @sell="handleShowSellDialog"
          @history="handleShowHistory"
          @analyze="handleAnalyze"
        />
      </el-col>
      <el-col :span="8">
        <PieChart :positions="portfolioStore.positions" />
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="24">
        <HistoryTable
          :transactions="portfolioStore.transactions"
          :loading="portfolioStore.loading"
          @refresh="handleRefreshHistory"
          @filter="handleFilterHistory"
        />
      </el-col>
    </el-row>

    <!-- 买入/卖出对话框 -->
    <TradeForm
      :visible="tradeDialogVisible"
      :type="tradeType"
      :ticker="selectedTicker"
      :loading="tradeLoading"
      @close="handleCloseTradeDialog"
      @submit="handleTradeSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { usePortfolioStore } from '../stores/portfolio'
import SummaryCard from '../components/portfolio/SummaryCard.vue'
import PositionTable from '../components/portfolio/PositionTable.vue'
import PieChart from '../components/portfolio/PieChart.vue'
import HistoryTable from '../components/portfolio/HistoryTable.vue'
import TradeForm from '../components/portfolio/TradeForm.vue'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const tradeDialogVisible = ref(false)
const tradeType = ref<'buy' | 'sell'>('buy')
const selectedTicker = ref('')
const tradeLoading = ref(false)

// 初始化加载数据
onMounted(async () => {
  await handleRefresh()
  await handleRefreshHistory()
})

// 刷新持仓数据
const handleRefresh = async () => {
  try {
    await portfolioStore.fetchPerformance()
  } catch (error) {
    ElMessage.error('加载持仓数据失败')
  }
}

// 刷新交易历史
const handleRefreshHistory = async () => {
  try {
    await portfolioStore.fetchTransactions()
  } catch (error) {
    ElMessage.error('加载交易历史失败')
  }
}

// 筛选交易历史
const handleFilterHistory = async (ticker: string) => {
  try {
    await portfolioStore.fetchTransactions(ticker || undefined)
  } catch (error) {
    ElMessage.error('筛选交易历史失败')
  }
}

// 显示买入对话框
const handleShowBuyDialog = () => {
  tradeType.value = 'buy'
  selectedTicker.value = ''
  tradeDialogVisible.value = true
}

// 显示卖出对话框
const handleShowSellDialog = (ticker: string) => {
  tradeType.value = 'sell'
  selectedTicker.value = ticker
  tradeDialogVisible.value = true
}

// 关闭交易对话框
const handleCloseTradeDialog = () => {
  tradeDialogVisible.value = false
  selectedTicker.value = ''
}

// 提交交易
const handleTradeSubmit = async (data: {
  ticker: string
  shares: number
  price: number
  trade_date?: string
  notes?: string
}) => {
  tradeLoading.value = true
  try {
    if (tradeType.value === 'buy') {
      await portfolioStore.buyStock(data)
      ElMessage.success('买入成功')
    } else {
      await portfolioStore.sellStock(data)
      ElMessage.success('卖出成功')
    }
    handleCloseTradeDialog()
    await handleRefreshHistory()
  } catch (error) {
    ElMessage.error(`${tradeType.value === 'buy' ? '买入' : '卖出'}失败`)
  } finally {
    tradeLoading.value = false
  }
}

// 查看交易历史
const handleShowHistory = async (ticker: string) => {
  await handleFilterHistory(ticker)
}

// 跳转到分析页面
const handleAnalyze = (ticker: string) => {
  router.push(`/analyze?ticker=${ticker}`)
}
</script>

<style scoped>
.portfolio-page {
  padding: 20px;
}
</style>
