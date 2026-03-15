<template>
  <div class="analysis-page">
    <el-row :gutter="24">
      <el-col :span="18">
        <SearchBar :loading="analysisStore.loading" @analyze="handleAnalyze" />
        <ProgressTracker
          :loading="analysisStore.loading"
          :progress="analysisStore.progress"
          :mode="currentMode"
        />
        <ReportCard :result="analysisStore.currentResult" />
      </el-col>
      <el-col :span="6">
        <HistoryList
          :history="analysisStore.history"
          @select="handleSelectHistory"
          @clear="handleClearHistory"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAnalysisStore } from '../stores/analysis'
import SearchBar from '../components/analysis/SearchBar.vue'
import ProgressTracker from '../components/analysis/ProgressTracker.vue'
import ReportCard from '../components/analysis/ReportCard.vue'
import HistoryList from '../components/analysis/HistoryList.vue'
import type { AnalysisMode, AnalysisHistory } from '../types/analysis'

const analysisStore = useAnalysisStore()
const currentMode = ref<AnalysisMode>('full')

const handleAnalyze = async (ticker: string, mode: AnalysisMode) => {
  currentMode.value = mode
  try {
    await analysisStore.analyze(ticker, mode)
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error('分析失败，请稍后重试')
  }
}

const handleSelectHistory = async (item: AnalysisHistory) => {
  await handleAnalyze(item.ticker, item.mode)
}

const handleClearHistory = () => {
  analysisStore.history = []
  ElMessage.success('已清空历史记录')
}
</script>

<style scoped>
.analysis-page {
  padding: 20px;
}
</style>
