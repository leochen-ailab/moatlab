<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="logo">
        <span class="logo-text">MoatLab</span>
      </div>
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        class="header-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/analyze">股票分析</el-menu-item>
        <el-menu-item index="/portfolio">持仓管理</el-menu-item>
        <el-menu-item index="/screen">股票筛选</el-menu-item>
        <el-menu-item index="/settings">设置</el-menu-item>
      </el-menu>
    </el-header>
    <el-container>
      <el-aside width="200px" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/analyze">
            <el-icon><TrendCharts /></el-icon>
            <span>股票分析</span>
          </el-menu-item>
          <el-menu-item index="/portfolio">
            <el-icon><Wallet /></el-icon>
            <span>持仓管理</span>
          </el-menu-item>
          <el-menu-item index="/screen">
            <el-icon><Search /></el-icon>
            <span>股票筛选</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, TrendCharts, Wallet, Search, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

const handleMenuSelect = (index: string) => {
  router.push(index)
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  background-color: #1e3a8a;
  color: white;
  padding: 0 20px;
}

.logo {
  margin-right: 40px;
}

.logo-text {
  font-size: 24px;
  font-weight: bold;
  color: #f59e0b;
}

.header-menu {
  flex: 1;
  background-color: transparent;
  border-bottom: none;
}

.header-menu .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.header-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #f59e0b;
}

.header-menu .el-menu-item.is-active {
  border-bottom-color: #f59e0b;
  color: #f59e0b;
}

.sidebar {
  background-color: #f3f4f6;
  border-right: 1px solid #e5e7eb;
}

.sidebar-menu {
  border-right: none;
}

.main-content {
  background-color: #ffffff;
  padding: 24px;
}
</style>
