<template>
  <el-card class="history-card">
    <template #header>
      <div class="card-header">
        <span>分析历史</span>
        <el-button size="small" text @click="$emit('clear')">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </template>
    <el-empty v-if="!history || history.length === 0" description="暂无分析历史" />
    <div v-else class="history-list">
      <div
        v-for="(item, index) in history"
        :key="index"
        class="history-item"
        @click="$emit('select', item)"
      >
        <div class="item-left">
          <span class="item-ticker">{{ item.ticker }}</span>
          <el-tag size="small" type="info">{{ getModeLabel(item.mode) }}</el-tag>
        </div>
        <div class="item-right">
          <el-tag
            v-if="item.recommendation"
            size="small"
            :type="getRecommendationType(item.recommendation)"
          >
            {{ item.recommendation }}
          </el-tag>
          <span class="item-time">{{ formatTime(item.timestamp) }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Delete } from '@element-plus/icons-vue'
import type { AnalysisHistory, AnalysisMode } from '../../types/analysis'

interface Props {
  history: AnalysisHistory[]
}

defineProps<Props>()
defineEmits<{
  select: [item: AnalysisHistory]
  clear: []
}>()

const getModeLabel = (mode: AnalysisMode): string => {
  const labels: Record<AnalysisMode, string> = {
    full: '全面',
    financial: '财务',
    valuation: '估值',
    moat: '护城河',
    management: '管理层',
  }
  return labels[mode] || mode
}

const getRecommendationType = (rec: string) => {
  if (rec === 'BUY') return 'success'
  if (rec === 'HOLD') return 'warning'
  if (rec === 'SELL') return 'danger'
  return 'info'
}

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.history-list {
  max-height: 500px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background-color: #f5f7fa;
}

.history-item:last-child {
  border-bottom: none;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-ticker {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-time {
  font-size: 12px;
  color: #909399;
}
</style>
