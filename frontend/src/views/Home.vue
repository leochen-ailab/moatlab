<template>
  <div class="home">
    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="quick-entry-card" shadow="hover" @click="navigateTo('/analyze')">
          <div class="card-content">
            <el-icon :size="48" color="#1e3a8a"><TrendCharts /></el-icon>
            <h3>股票分析</h3>
            <p>深度分析股票的财务、估值、护城河和管理层</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="quick-entry-card" shadow="hover" @click="navigateTo('/portfolio')">
          <div class="card-content">
            <el-icon :size="48" color="#10b981"><Wallet /></el-icon>
            <h3>持仓管理</h3>
            <p>记录交易、追踪收益、查看持仓表现</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="quick-entry-card" shadow="hover" @click="navigateTo('/screen')">
          <div class="card-content">
            <el-icon :size="48" color="#f59e0b"><Search /></el-icon>
            <h3>股票筛选</h3>
            <p>按价值投资标准筛选优质股票</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>欢迎使用 MoatLab</span>
            </div>
          </template>
          <div class="welcome-content">
            <p>MoatLab 是一个基于巴菲特和段永平价值投资理念的智能分析系统。</p>
            <p>通过 AI 驱动的多维度分析，帮助您发现具有护城河的优质企业。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { TrendCharts, Wallet, Search } from '@element-plus/icons-vue'

const router = useRouter()

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.quick-entry-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.quick-entry-card:hover {
  transform: translateY(-4px);
}

.card-content {
  text-align: center;
  padding: 20px;
}

.card-content h3 {
  margin: 16px 0 8px;
  font-size: 20px;
  color: #1f2937;
}

.card-content p {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.welcome-content {
  line-height: 1.8;
  color: #4b5563;
}
</style>
