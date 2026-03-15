<template>
  <div class="screener-page">
    <el-row :gutter="24">
      <el-col :span="8">
        <FilterForm
          :loading="screenerStore.loading"
          @screen="handleScreen"
          @reset="handleReset"
        />
      </el-col>
      <el-col :span="16">
        <ResultCard
          :result="screenerStore.result"
          :loading="screenerStore.loading"
          @refresh="handleRefresh"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { useScreenerStore } from '../stores/screener'
import FilterForm from '../components/screener/FilterForm.vue'
import ResultCard from '../components/screener/ResultCard.vue'
import type { ScreenCriteria } from '../types/screener'

const screenerStore = useScreenerStore()

const handleScreen = async (criteria: ScreenCriteria) => {
  try {
    await screenerStore.screen(criteria)
    ElMessage.success('筛选完成')
  } catch (error) {
    ElMessage.error('筛选失败，请稍后重试')
  }
}

const handleReset = () => {
  screenerStore.reset()
  ElMessage.success('已重置筛选条件')
}

const handleRefresh = async () => {
  if (Object.keys(screenerStore.criteria).length === 0) {
    ElMessage.warning('请先设置筛选条件')
    return
  }
  await handleScreen(screenerStore.criteria)
}
</script>

<style scoped>
.screener-page {
  padding: 20px;
}
</style>
