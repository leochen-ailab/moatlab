<template>
  <el-card class="history-table-card">
    <template #header>
      <div class="card-header">
        <span>交易历史</span>
        <div class="header-actions">
          <el-input
            v-model="filterTicker"
            placeholder="筛选股票代码"
            clearable
            style="width: 200px; margin-right: 8px"
            @change="handleFilter"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button size="small" @click="$emit('refresh')">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </template>
    <el-table
      :data="transactions"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="ticker" label="股票代码" width="120" />
      <el-table-column prop="action" label="操作" width="100">
        <template #default="{ row }">
          <el-tag :type="row.action === 'buy' ? 'success' : 'danger'" size="small">
            {{ row.action === 'buy' ? '买入' : '卖出' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="shares" label="数量" width="120" align="right">
        <template #default="{ row }">
          {{ formatNumber(row.shares, 0) }}
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="120" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.price) }}
        </template>
      </el-table-column>
      <el-table-column label="总金额" width="140" align="right">
        <template #default="{ row }">
          {{ formatCurrency(row.shares * row.price) }}
        </template>
      </el-table-column>
      <el-table-column prop="trade_date" label="交易日期" width="120">
        <template #default="{ row }">
          {{ formatDate(row.trade_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" min-width="200" show-overflow-tooltip />
    </el-table>
    <el-empty v-if="!transactions || transactions.length === 0" description="暂无交易记录" />
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { formatCurrency, formatNumber, formatDate } from '../../utils/format'
import type { Transaction } from '../../types/portfolio'

interface Props {
  transactions: Transaction[]
  loading?: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  refresh: []
  filter: [ticker: string]
}>()

const filterTicker = ref('')

const handleFilter = () => {
  emit('filter', filterTicker.value)
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

.header-actions {
  display: flex;
  align-items: center;
}
</style>
