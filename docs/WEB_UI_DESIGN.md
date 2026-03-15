# MoatLab Web UI 设计方案

> 最后更新：2026-03-15

---

## Context
MoatLab 目前是一个纯后端系统，拥有完整的 FastAPI 接口和 CLI 工具，但缺少 Web 前端界面。用户需要通过命令行或直接调用 API 来使用系统功能。本设计旨在提供一个现代化的 Web UI，让用户能够通过浏览器直观地进行股票分析、持仓管理和股票筛选。

---

## 技术栈选择

### 前端框架：**Vue 3 + TypeScript**
- **理由**：轻量、渐进式、学习曲线平缓，适合快速开发
- 组合式 API (Composition API) 提供更好的类型推断和代码组织
- 生态成熟，与 FastAPI 后端集成简单

### UI 组件库：**Element Plus**
- 企业级组件库，开箱即用
- 中文文档完善，符合项目中文优先的设计
- 提供表格、表单、图表等完整组件

### 构建工具：**Vite**
- 极速的开发服务器和构建速度
- 原生 ESM 支持，TypeScript 开箱即用
- Vue 官方推荐

### 图表库：**ECharts**
- 功能强大的数据可视化库
- 适合展示财务数据、持仓分析、历史价格走势
- 中文文档完善

### HTTP 客户端：**Axios**
- 简洁的 API 调用封装
- 拦截器支持（统一错误处理、loading 状态）

### 状态管理：**Pinia**
- Vue 3 官方推荐的状态管理库
- TypeScript 支持优秀
- 用于管理持仓数据、分析结果缓存

---

## 页面结构设计

### 1. 布局框架
```
┌─────────────────────────────────────────────┐
│  Header: MoatLab Logo + 导航菜单             │
├──────────┬──────────────────────────────────┤
│          │                                  │
│  侧边栏   │         主内容区                  │
│  导航     │                                  │
│          │                                  │
│  - 股票分析│                                  │
│  - 持仓管理│                                  │
│  - 股票筛选│                                  │
│  - 设置   │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

### 2. 核心页面（3个主要功能页）

#### **页面 1：股票分析 (Stock Analysis)**
**路由**: `/analyze`

**功能模块**：
1. **搜索区域**（顶部）
   - 股票代码输入框（支持自动补全）
   - 分析模式选择：全面分析 / 财务分析 / 估值分析 / 护城河分析 / 管理层分析
   - "开始分析" 按钮

2. **分析进度区域**（分析中显示）
   - 进度条显示当前执行的 Agent
   - 实时日志流（WebSocket 或轮询）
   - 预计剩余时间

3. **分析结果展示区域**（分析完成后）
   - **顶部卡片**：投资建议（BUY/HOLD/SELL/PASS）+ 核心结论
   - **Tab 切换**：
     - 综合报告：完整的分析报告（Markdown 渲染）
     - 财务数据：表格展示财务指标（ROE、ROIC、利润率等）
     - 估值分析：DCF 估值、安全边际、PE/PB 百分位
     - 护城河：护城河类型雷达图 + 详细说明
     - 管理层：管理层评分 + 资本配置历史
   - **图表可视化**：
     - 历史价格走势图（ECharts 折线图）
     - 财务指标趋势图（5年数据）
     - 估值对比图（当前价格 vs 内在价值）

4. **历史分析记录**（侧边栏或底部）
   - 最近分析的股票列表
   - 点击快速加载历史结果

**UI 设计要点**：
- 分析结果用卡片布局，清晰分层
- 投资建议用醒目的颜色标识（绿色=BUY，黄色=HOLD，红色=SELL，灰色=PASS）
- 支持导出 PDF 报告

---

#### **页面 2：持仓管理 (Portfolio Management)**
**路由**: `/portfolio`

**功能模块**：
1. **持仓概览卡片**（顶部）
   - 总成本、总市值、总收益、收益率（大字号显示）
   - 盈利/亏损持仓数量统计
   - 饼图：持仓分布（按市值占比）

2. **持仓列表表格**（中部）
   - 列：股票代码、公司名称、持仓数量、平均成本、当前价格、市值、盈亏金额、盈亏比例、首次买入日期
   - 支持排序（按盈亏、市值、代码等）
   - 行操作按钮：卖出、查看交易历史、分析
   - 颜色标识：盈利行绿色背景，亏损行红色背景

3. **交易操作区域**（右侧抽屉或弹窗）
   - **买入表单**：股票代码、数量、价格、交易日期、备注
   - **卖出表单**：选择持仓、数量、价格、交易日期、备注
   - 表单验证：数量不能超过持仓、价格必须为正数等

4. **交易历史**（底部或独立 Tab）
   - 表格展示所有交易记录
   - 筛选：按股票代码、交易类型（买入/卖出）、日期范围
   - 导出功能（CSV）

**UI 设计要点**：
- 实时刷新市场价格（每分钟或手动刷新按钮）
- 盈亏数据用醒目的颜色和图标
- 移动端适配：卡片式布局

---

#### **页面 3：股票筛选 (Stock Screener)**
**路由**: `/screen`

**功能模块**：
1. **筛选条件表单**（左侧或顶部）
   - ROE 范围（最小值）
   - 负债率范围（最大值）
   - 毛利率范围（最小值）
   - PE 范围（最小值、最大值）
   - 市值范围
   - 股息率范围
   - 行业选择（多选下拉框）
   - "开始筛选" 按钮
   - "重置条件" 按钮

2. **筛选结果表格**（右侧或下方）
   - 列：股票代码、公司名称、ROE、负债率、毛利率、PE、市值、股息率、行业
   - 默认按 ROE 降序排列
   - 支持多列排序
   - 行操作：快速分析、添加到持仓

3. **结果统计**（顶部卡片）
   - 符合条件的股票数量
   - 平均 ROE、平均 PE 等统计指标

4. **保存筛选方案**（可选功能）
   - 保存常用筛选条件为模板
   - 快速加载预设方案

**UI 设计要点**：
- 筛选条件用折叠面板，节省空间
- 结果表格支持分页（每页 20 条）
- 提供"一键分析前 10 名"功能

---

### 3. 辅助页面

#### **设置页面** (`/settings`)
- API 配置：Claude API Key、数据库路径
- 显示偏好：主题（亮色/暗色）、语言（中文/英文）
- 数据刷新频率设置

#### **首页/仪表盘** (`/`)
- 快速入口：分析、持仓、筛选
- 最近分析的股票卡片
- 持仓概览摘要
- 市场行情概览（可选）

---

## 前端项目结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.ts                 # 入口文件
│   ├── App.vue                 # 根组件
│   ├── router/
│   │   └── index.ts            # 路由配置
│   ├── stores/
│   │   ├── portfolio.ts        # 持仓状态管理
│   │   ├── analysis.ts         # 分析结果缓存
│   │   └── settings.ts         # 用户设置
│   ├── api/
│   │   ├── client.ts           # Axios 实例配置
│   │   ├── portfolio.ts        # 持仓 API 封装
│   │   ├── analysis.ts         # 分析 API 封装
│   │   └── screener.ts         # 筛选 API 封装
│   ├── views/
│   │   ├── Home.vue            # 首页
│   │   ├── Analysis.vue        # 股票分析页
│   │   ├── Portfolio.vue       # 持仓管理页
│   │   ├── Screener.vue        # 股票筛选页
│   │   └── Settings.vue        # 设置页
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.vue      # 顶部导航
│   │   │   ├── Sidebar.vue     # 侧边栏
│   │   │   └── Layout.vue      # 布局容器
│   │   ├── analysis/
│   │   │   ├── SearchBar.vue   # 搜索栏
│   │   │   ├── ProgressTracker.vue  # 分析进度
│   │   │   ├── ReportCard.vue  # 报告卡片
│   │   │   └── ChartPanel.vue  # 图表面板
│   │   ├── portfolio/
│   │   │   ├── SummaryCard.vue # 概览卡片
│   │   │   ├── PositionTable.vue  # 持仓表格
│   │   │   ├── TradeForm.vue   # 交易表单
│   │   │   └── HistoryTable.vue   # 历史记录
│   │   └── screener/
│   │       ├── FilterForm.vue  # 筛选表单
│   │       └── ResultTable.vue # 结果表格
│   ├── types/
│   │   ├── portfolio.ts        # 持仓类型定义
│   │   ├── analysis.ts         # 分析类型定义
│   │   └── api.ts              # API 响应类型
│   └── utils/
│       ├── format.ts           # 格式化工具（金额、百分比）
│       └── chart.ts            # ECharts 配置工具
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 后端改动（最小化）

### 1. 静态文件服务
在 `server.py` 中添加静态文件挂载：
```python
from fastapi.staticfiles import StaticFiles

# 挂载前端构建产物
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

### 2. CORS 配置（开发环境）
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. WebSocket 支持（可选，用于实时分析进度）
```python
from fastapi import WebSocket

@app.websocket("/ws/analyze/{ticker}")
async def analyze_websocket(websocket: WebSocket, ticker: str):
    await websocket.accept()
    # 流式推送分析进度
```

---

## 开发计划

### Phase 1: 基础框架搭建
1. 初始化 Vite + Vue 3 + TypeScript 项目
2. 安装依赖：Element Plus、ECharts、Axios、Pinia、Vue Router
3. 配置路由和布局组件
4. 封装 API 客户端（Axios 实例 + 拦截器）

### Phase 2: 持仓管理页面
1. 实现持仓概览卡片（调用 `/api/portfolio` 和 `/api/portfolio/performance`）
2. 实现持仓列表表格（实时价格刷新）
3. 实现买入/卖出表单（调用 `/api/portfolio/buy` 和 `/api/portfolio/sell`）
4. 实现交易历史表格（调用 `/api/portfolio/history`）

### Phase 3: 股票分析页面
1. 实现搜索栏和模式选择
2. 实现分析进度跟踪（轮询或 WebSocket）
3. 实现分析结果展示（Tab 切换、Markdown 渲染）
4. 实现图表可视化（ECharts 集成）

### Phase 4: 股票筛选页面
1. 实现筛选条件表单
2. 实现结果表格（调用 `/api/screen`）
3. 实现快速分析功能

### Phase 5: 优化与部署
1. 响应式设计（移动端适配）
2. 错误处理和 Loading 状态
3. 构建生产版本（`npm run build`）
4. 集成到 FastAPI 静态文件服务

---

## 关键文件路径

**后端**：
- `/Users/bytedance/moatlab-workspace/moatlab/src/moatlab/server.py` — FastAPI 应用
- `/Users/bytedance/moatlab-workspace/moatlab/src/moatlab/cli.py` — CLI 入口

**前端**（待创建）：
- `/Users/bytedance/moatlab-workspace/moatlab/frontend/` — 前端项目根目录

---

## UI 设计风格建议

### 配色方案
- **主色调**：深蓝色（#1E3A8A）— 专业、稳重
- **辅助色**：金色（#F59E0B）— 财富、价值
- **成功色**：绿色（#10B981）— 盈利
- **警告色**：红色（#EF4444）— 亏损
- **中性色**：灰色系（#F3F4F6, #6B7280）

### 字体
- 中文：思源黑体 / 苹方
- 英文/数字：Inter / Roboto
- 代码：JetBrains Mono

### 组件风格
- 圆角：8px（卡片）、4px（按钮）
- 阴影：轻微阴影增强层次感
- 间距：统一使用 8px 倍数（8, 16, 24, 32）

---

## 验证方案

### 功能测试
1. **持仓管理**：
   - 添加持仓 → 验证表格更新
   - 卖出持仓 → 验证数量减少、盈亏计算正确
   - 查看交易历史 → 验证记录完整

2. **股票分析**：
   - 输入 AAPL → 选择"全面分析" → 验证进度显示 → 验证报告完整性
   - 切换不同分析模式 → 验证结果差异

3. **股票筛选**：
   - 设置 ROE > 15% → 验证结果符合条件
   - 多条件组合筛选 → 验证逻辑正确

### 性能测试
- 持仓列表加载时间 < 1s
- 分析请求响应时间 < 30s（取决于 Claude API）
- 图表渲染流畅（60fps）

### 兼容性测试
- 浏览器：Chrome、Firefox、Safari、Edge（最新版本）
- 屏幕尺寸：桌面（1920x1080）、平板（768px）、手机（375px）

---

## 可选增强功能（Phase 6+）

1. **实时市场数据**：WebSocket 推送股价变动
2. **智能提醒**：持仓盈亏达到阈值时通知
3. **对比分析**：同时分析多只股票并对比
4. **自定义仪表盘**：用户可拖拽组件自定义首页
5. **暗色模式**：支持主题切换
6. **多语言**：中英文切换
7. **导出功能**：分析报告导出 PDF、持仓导出 Excel
8. **移动端 App**：使用 Capacitor 打包为原生应用

---

## 总结

这是一个**渐进式、模块化**的 Web UI 设计方案：
- **技术栈成熟**：Vue 3 + Element Plus + ECharts，开发效率高
- **功能完整**：覆盖分析、持仓、筛选三大核心场景
- **后端改动最小**：仅需添加静态文件服务和 CORS 配置
- **可扩展性强**：预留 WebSocket、多语言、暗色模式等增强功能接口

建议先实现 Phase 1-4（核心功能），验证可行性后再考虑 Phase 5-6（优化和增强）。
