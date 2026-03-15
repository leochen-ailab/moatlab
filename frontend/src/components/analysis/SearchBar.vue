<template>
  <el-card class="search-bar-card">
    <el-form :inline="true" :model="formData" @submit.prevent="handleSubmit">
      <el-form-item label="股票代码">
        <el-input
          v-model="formData.ticker"
          placeholder="例如：AAPL"
          style="width: 200px"
          clearable
          @keyup.enter="handleSubmit"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="分析模式">
        <el-select v-model="formData.mode" style="width: 180px">
          <el-option label="全面分析" value="full" />
          <el-option label="财务分析" value="financial" />
          <el-option label="估值分析" value="valuation" />
          <el-option label="护城河分析" value="moat" />
          <el-option label="管理层分析" value="management" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          <el-icon><Search /></el-icon>
          开始分析
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { AnalysisMode } from '../../types/analysis'

interface Props {
  loading?: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  analyze: [ticker: string, mode: AnalysisMode]
}>()

const formData = reactive({
  ticker: '',
  mode: 'full' as AnalysisMode,
})

const handleSubmit = () => {
  if (!formData.ticker.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  emit('analyze', formData.ticker.toUpperCase(), formData.mode)
}
</script>

<style scoped>
.search-bar-card {
  margin-bottom: 24px;
}

:deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
}
</style>
