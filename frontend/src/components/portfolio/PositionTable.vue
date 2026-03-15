<template>
  <el-card class="position-table-card">
    <template #header>
      <div class="card-header">
        <span>持仓列表</span>
        <el-button type="primary" size="small" @click="$emit('add')">
          <el-icon><Plus /></el-icon>
          买入
        </el-button>
      </div>
    </template>
    <el-table
      :data="positions"
      style="width: 100%"
      :default-sort="{ prop: 'profit_loss_pct', order: 'descending' }"
      v-loading="loading"
      :row-class-name="getRowClassName"
    >
      <el-table-column prop="ticker" label="股票代码" width="120" sortable />
      <el-table-column prop="company_name" label="公司名称" width="180" />
      <el-table-column prop="shares" label="持仓数量" width="120" sortable align="right">
        <template #default="{ row }">
          {{ formatNumber(row.shares, 0) }}
        </template>
      </el-table-column>
      <el-table-column prop="avg_cost" label="平均成本" width="120" sortable align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.avg_cost) }}
        </template>
      </el-table-column>
      <el-table-column prop="current_price" label="当前价格" width="120" sortable align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.current_price) }}
        </template>
      </el-table-column>
      <el-table-column prop="market_value" label="市值" width="140" sortable align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.market_value) }}
        </template>
      </el-table-column>
      <el-table-column prop="profit_loss" label="盈亏金额" width="140" sortable align="right">
        <template #default="{ row }">
          <span :class="row.profit_loss >= 0 ? 'profit' : 'loss'">
            {{ formatCurrency(row.profit_loss) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="profit_loss_pct" label="盈亏比例" width="120" sortable align="right">
        <template #default="{ row }">
          <span :class="row.profit_loss_pct >= 0 ? 'profit' : 'loss'">
            {{ formatPercent(row.profit_loss_pct) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="first_buy_date" label="首次买入" width="120">
        <template #default="{ row }">
          {{ formatDate(row.first_buy_date) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$emit('sell', row.ticker)">卖出</el-button>
          <el-button size="small" @click="$emit('history', row.ticker)">历史</el-button>
          <el-button size="small" type="primary" @click="$emit('analyze', row.ticker)">
            分析
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!positions || positions.length === 0" description="暂无持仓" />
  </el-card>
</template>

<script setup lang="ts">
import { Plus } from '@element-plus/icons-vue'
import { formatCurrency, formatPercent, formatNumber, formatDate } from '../../utils/format'
import type { Position } from '../../types/portfolio'

interface Props {
  positions: Position[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  add: []
  sell: [ticker: string]
  history: [ticker: string]
  analyze: [ticker: string]
}>()

const getRowClassName = ({ row }: { row: Position }) => {
  if (!row.profit_loss) return ''
  return row.profit_loss >= 0 ? 'profit-row' : 'loss-row'
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

.profit {
  color: #10b981;
  font-weight: 600;
}

.loss {
  color: #ef4444;
  font-weight: 600;
}

:deep(.profit-row) {
  background-color: #f0fdf4;
}

:deep(.loss-row) {
  background-color: #fef2f2;
}
</style>
