<template>
  <el-card class="pie-chart-card">
    <template #header>
      <div class="card-header">
        <span>持仓分布</span>
      </div>
    </template>
    <div ref="chartRef" style="width: 100%; height: 400px"></div>
    <el-empty v-if="!positions || positions.length === 0" description="暂无持仓数据" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import type { Position } from '../../types/portfolio'

interface Props {
  positions: Position[]
}

const props = defineProps<Props>()

const chartRef = ref<HTMLElement>()
let chartInstance: ECharts | null = null

const initChart = () => {
  if (!chartRef.value || !props.positions || props.positions.length === 0) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const data = props.positions
    .filter(p => p.market_value && p.market_value > 0)
    .map(p => ({
      name: p.ticker,
      value: p.market_value,
    }))
    .sort((a, b) => b.value - a.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ${c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: data.map(d => d.name),
    },
    series: [
      {
        name: '市值',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
          },
        },
        labelLine: {
          show: false,
        },
        data: data,
      },
    ],
  }

  chartInstance.setOption(option)
}

onMounted(() => {
  nextTick(() => {
    initChart()
  })

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})

watch(() => props.positions, () => {
  nextTick(() => {
    initChart()
  })
}, { deep: true })
</script>

<style scoped>
.card-header {
  font-size: 16px;
  font-weight: 600;
}
</style>
