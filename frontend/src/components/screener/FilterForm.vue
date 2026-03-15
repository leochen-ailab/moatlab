<template>
  <el-card class="filter-form-card">
    <template #header>
      <div class="card-header">
        <span>筛选条件</span>
        <el-button size="small" text @click="handleReset">
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
      </div>
    </template>
    <el-form :model="formData" label-width="120px" label-position="left">
      <el-form-item label="ROE 最小值">
        <el-input-number
          v-model="formData.roe_min"
          :min="0"
          :max="1"
          :step="0.01"
          :precision="2"
          placeholder="例如：0.15"
          style="width: 100%"
        />
        <span class="form-hint">（15% = 0.15）</span>
      </el-form-item>
      <el-form-item label="负债率最大值">
        <el-input-number
          v-model="formData.debt_to_equity_max"
          :min="0"
          :step="0.1"
          :precision="2"
          placeholder="例如：0.5"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="毛利率最小值">
        <el-input-number
          v-model="formData.gross_margin_min"
          :min="0"
          :max="1"
          :step="0.01"
          :precision="2"
          placeholder="例如：0.4"
          style="width: 100%"
        />
        <span class="form-hint">（40% = 0.4）</span>
      </el-form-item>
      <el-form-item label="PE 最大值">
        <el-input-number
          v-model="formData.pe_max"
          :min="0"
          :step="1"
          :precision="0"
          placeholder="例如：25"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="行业">
        <el-input
          v-model="formData.sector"
          placeholder="例如：Technology"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading" style="width: 100%">
          <el-icon><Search /></el-icon>
          开始筛选
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { RefreshLeft, Search } from '@element-plus/icons-vue'
import type { ScreenCriteria } from '../../types/screener'

interface Props {
  loading?: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  screen: [criteria: ScreenCriteria]
  reset: []
}>()

const formData = reactive<ScreenCriteria>({
  roe_min: undefined,
  debt_to_equity_max: undefined,
  gross_margin_min: undefined,
  pe_max: undefined,
  sector: undefined,
})

const handleSubmit = () => {
  // 过滤掉未设置的条件
  const criteria: ScreenCriteria = {}
  if (formData.roe_min !== undefined && formData.roe_min !== null) {
    criteria.roe_min = formData.roe_min
  }
  if (formData.debt_to_equity_max !== undefined && formData.debt_to_equity_max !== null) {
    criteria.debt_to_equity_max = formData.debt_to_equity_max
  }
  if (formData.gross_margin_min !== undefined && formData.gross_margin_min !== null) {
    criteria.gross_margin_min = formData.gross_margin_min
  }
  if (formData.pe_max !== undefined && formData.pe_max !== null) {
    criteria.pe_max = formData.pe_max
  }
  if (formData.sector && formData.sector.trim()) {
    criteria.sector = formData.sector.trim()
  }
  
  emit('screen', criteria)
}

const handleReset = () => {
  formData.roe_min = undefined
  formData.debt_to_equity_max = undefined
  formData.gross_margin_min = undefined
  formData.pe_max = undefined
  formData.sector = undefined
  emit('reset')
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

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
