<template>
  <el-card v-if="result" class="report-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span class="ticker">{{ result.ticker }}</span>
          <el-tag v-if="result.mode" size="small" type="info">
            {{ getModeLabel(result.mode) }}
          </el-tag>
        </div>
        <div class="header-right">
          <el-tag
            v-if="recommendation"
            :type="getRecommendationType(recommendation)"
            size="large"
            effect="dark"
          >
            {{ recommendation }}
          </el-tag>
        </div>
      </div>
    </template>

    <div class="report-content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="分析报告" name="report">
          <div class="markdown-content" v-html="renderedMarkdown"></div>
        </el-tab-pane>
        <el-tab-pane label="原始数据" name="raw">
          <pre class="raw-content">{{ result.result }}</pre>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AnalysisResult, AnalysisMode } from '../../types/analysis'

interface Props {
  result: AnalysisResult | null
}

const props = defineProps<Props>()

const activeTab = ref('report')

const recommendation = computed(() => {
  if (!props.result?.result) return null
  const text = props.result.result.toUpperCase()
  if (text.includes('BUY') || text.includes('买入')) return 'BUY'
  if (text.includes('HOLD') || text.includes('持有')) return 'HOLD'
  if (text.includes('SELL') || text.includes('卖出')) return 'SELL'
  if (text.includes('PASS') || text.includes('观望')) return 'PASS'
  return null
})

const renderedMarkdown = computed(() => {
  if (!props.result?.result) return ''
  // 简单的 Markdown 渲染（换行和段落）
  return props.result.result
    .split('\n\n')
    .map(para => `<p>${para.replace(/\n/g, '<br>')}</p>`)
    .join('')
})

const getModeLabel = (mode: AnalysisMode): string => {
  const labels: Record<AnalysisMode, string> = {
    full: '全面分析',
    financial: '财务分析',
    valuation: '估值分析',
    moat: '护城河分析',
    management: '管理层分析',
  }
  return labels[mode] || mode
}

const getRecommendationType = (rec: string) => {
  if (rec === 'BUY') return 'success'
  if (rec === 'HOLD') return 'warning'
  if (rec === 'SELL') return 'danger'
  return 'info'
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ticker {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.report-content {
  min-height: 400px;
}

.markdown-content {
  line-height: 1.8;
  color: #303133;
}

.markdown-content :deep(p) {
  margin: 12px 0;
}

.raw-content {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
