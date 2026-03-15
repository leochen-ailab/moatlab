<template>
  <el-card class="result-card">
    <template #header>
      <div class="card-header">
        <span>筛选结果</span>
        <el-button size="small" @click="$emit('refresh')" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>
    
    <el-empty v-if="!result" description="请设置筛选条件并开始筛选" />
    
    <div v-else class="result-content">
      <div class="result-text">
        <pre>{{ result.result }}</pre>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Refresh } from '@element-plus/icons-vue'
import type { ScreenResponse } from '../../types/screener'

interface Props {
  result: ScreenResponse | null
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  refresh: []
}>()
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.result-content {
  min-height: 400px;
}

.result-text {
  line-height: 1.8;
}

.result-text pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
  color: #303133;
}
</style>
