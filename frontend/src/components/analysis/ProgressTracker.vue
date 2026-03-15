<template>
  <el-card v-if="loading" class="progress-card">
    <div class="progress-content">
      <el-icon class="loading-icon" :size="40"><Loading /></el-icon>
      <div class="progress-text">
        <h3>正在分析中...</h3>
        <p>{{ statusText }}</p>
      </div>
      <el-progress :percentage="progress" :stroke-width="8" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  loading: boolean
  progress: number
  mode?: string
}

const props = defineProps<Props>()

const statusText = computed(() => {
  if (props.progress < 20) return '正在获取股票数据...'
  if (props.progress < 40) return '正在分析财务指标...'
  if (props.progress < 60) return '正在评估投资价值...'
  if (props.progress < 80) return '正在生成分析报告...'
  if (props.progress < 100) return '即将完成...'
  return '分析完成'
})
</script>

<style scoped>
.progress-card {
  margin-bottom: 24px;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.loading-icon {
  color: #409eff;
  margin-bottom: 16px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-text {
  text-align: center;
  margin-bottom: 20px;
}

.progress-text h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.progress-text p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

:deep(.el-progress) {
  width: 100%;
}
</style>
