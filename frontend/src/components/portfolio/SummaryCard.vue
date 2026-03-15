<template>
  <el-card class="summary-card">
    <template #header>
      <div class="card-header">
        <span>持仓概览</span>
        <el-button type="primary" size="small" @click="refresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>
    <el-row :gutter="24" v-if="summary">
      <el-col :span="6">
        <div class="summary-item">
          <div class="label">总成本</div>
          <div class="value">{{ formatCurrency(summary.total_cost) }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-item">
          <div class="label">总市值</div>
          <div class="value">{{ formatCurrency(summary.total_market_value) }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-item">
          <div class="label">总收益</div>
          <div class="value" :class="profitClass">
            {{ formatCurrency(summary.total_profit_loss) }}
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="summary-item">
          <div class="label">收益率</div>
          <div class="value" :class="profitClass">
            {{ formatPercent(summary.total_return_pct) }}
          </div>
        </div>
      </el-col>
    </el-row>
    <el-divider />
    <el-row :gutter="24" v-if="summary">
      <el-col :span="8">
        <div class="summary-item">
          <div class="label">持仓数量</div>
          <div class="value small">{{ summary.position_count }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="summary-item">
          <div class="label">盈利持仓</div>
          <div class="value small profit">{{ summary.winners }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="summary-item">
          <div class="label">亏损持仓</div>
          <div class="value small loss">{{ summary.losers }}</div>
        </div>
      </el-col>
    </el-row>
    <el-empty v-else description="暂无持仓数据" />
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { formatCurrency, formatPercent } from '../../utils/format'
import type { PortfolioSummary } from '../../types/portfolio'

interface Props {
  summary: PortfolioSummary | null
  loading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  refresh: []
}>()

const profitClass = computed(() => {
  if (!props.summary) return ''
  return props.summary.total_profit_loss >= 0 ? 'profit' : 'loss'
})

const refresh = () => {
  emit('refresh')
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

.summary-item {
  text-align: center;
  padding: 16px 0;
}

.summary-item .label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.summary-item .value.small {
  font-size: 24px;
}

.summary-item .value.profit {
  color: #10b981;
}

.summary-item .value.loss {
  color: #ef4444;
}
</style>
