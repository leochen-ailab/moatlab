<template>
  <el-dialog
    :model-value="visible"
    :title="type === 'buy' ? '买入股票' : '卖出股票'"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="股票代码" prop="ticker">
        <el-input
          v-model="formData.ticker"
          placeholder="例如：AAPL"
          :disabled="type === 'sell'"
        />
      </el-form-item>
      <el-form-item label="数量" prop="shares">
        <el-input-number
          v-model="formData.shares"
          :min="1"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="价格" prop="price">
        <el-input-number
          v-model="formData.price"
          :min="0.01"
          :precision="2"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="交易日期" prop="trade_date">
        <el-date-picker
          v-model="formData.trade_date"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="可选"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

interface Props {
  visible: boolean
  type: 'buy' | 'sell'
  ticker?: string
  loading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  submit: [data: {
    ticker: string
    shares: number
    price: number
    trade_date?: string
    notes?: string
  }]
}>()

const formRef = ref<FormInstance>()
const formData = reactive({
  ticker: '',
  shares: 1,
  price: 0,
  trade_date: new Date().toISOString().split('T')[0],
  notes: '',
})

const rules: FormRules = {
  ticker: [
    { required: true, message: '请输入股票代码', trigger: 'blur' },
    { pattern: /^[A-Z]+$/, message: '股票代码必须为大写字母', trigger: 'blur' },
  ],
  shares: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' },
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' },
  ],
}

// 监听 ticker prop 变化（用于卖出时预填）
watch(() => props.ticker, (newTicker) => {
  if (newTicker && props.type === 'sell') {
    formData.ticker = newTicker
  }
}, { immediate: true })

// 监听 visible 变化，重置表单
watch(() => props.visible, (newVisible) => {
  if (newVisible && props.type === 'buy') {
    formData.ticker = ''
    formData.shares = 1
    formData.price = 0
    formData.trade_date = new Date().toISOString().split('T')[0]
    formData.notes = ''
  }
})

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    emit('submit', {
      ticker: formData.ticker.toUpperCase(),
      shares: formData.shares,
      price: formData.price,
      trade_date: formData.trade_date,
      notes: formData.notes || undefined,
    })
  } catch (error) {
    ElMessage.error('请检查表单输入')
  }
}
</script>
