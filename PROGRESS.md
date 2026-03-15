# MoatLab — 项目进度报告

> 最后更新：2026-03-15

---

## 总体进度

| 阶段 | 状态 | 说明 |
|------|------|------|
| Phase 1 — 单股分析 CLI (MVP) | ✅ 完成 | v0.1.0 |
| Phase 2 — 完整分析链 | ✅ 完成 | v0.2.0 |
| Phase 3 — 持仓管理 + Web API | ✅ 完成 | v0.3.0 |
| Phase 4 — Web UI 前端 | 🚧 进行中 | v0.4.0 |

---

## Phase 1 — 单股分析 CLI (MVP) ✅

**目标**：跑通单股财务分析 + 估值的最小可用版本

| 交付项 | 状态 | PR |
|--------|------|----|
| 项目脚手架（pyproject.toml、目录结构、配置管理） | ✅ | #1 |
| BaseAgent 基类 + Claude API tool_use 循环 | ✅ | #2 |
| yfinance 市场数据工具封装（market_data.py） | ✅ | #2 |
| FinancialAgent + 财务分析提示词 | ✅ | #2 |
| DCF/Owner Earnings 计算器（calculator.py） | ✅ | #3 |
| ValuationAgent + 估值分析提示词 | ✅ | #3 |
| CLI 入口：`moatlab analyze AAPL -m financial/valuation` | ✅ | #3 |

---

## Phase 2 — 完整分析链 ✅

**目标**：7 个 Agent 全部就位，Orchestrator 编排完整分析流程

| 交付项 | 状态 | PR |
|--------|------|----|
| MoatAgent — 护城河分析 | ✅ | #4 |
| ManagementAgent — 管理层分析 | ✅ | #5 |
| DecisionAgent — 投资决策（纯推理，无工具） | ✅ | #6 |
| Orchestrator 编排引擎（并行 + 串行 DAG 调度） | ✅ | #6 |
| 全链路 CLI：`moatlab analyze AAPL`（full 模式） | ✅ | #6 |
| ScreenerAgent + 股票筛选工具 | ✅ | #7 |
| CLI 筛选命令：`moatlab screen --roe-min 0.15` | ✅ | #7 |

---

## Phase 3 — 持仓管理 + Web API ✅

**目标**：支持持仓记录、收益追踪、AI 持仓回顾，并提供 Web API

| 交付项 | 状态 | PR |
|--------|------|----|
| SQLite 持久化层 + 数据模型 | ✅ | #8 |
| 持仓管理工具函数（买入/卖出/查询/业绩） | ✅ | #9 |
| PortfolioAgent + 持仓管理提示词 | ✅ | #10 |
| CLI 持仓命令：`moatlab portfolio add/sell/list/review/history` | ✅ | #11 |
| FastAPI Web API + `moatlab serve` 命令 | ✅ | #12 |
| 测试（21 个测试用例） + 文档更新 | ✅ | #13 |

---

## Phase 4 — Web UI 前端 🚧

**目标**：提供现代化的 Web 界面，支持股票分析、持仓管理、股票筛选

### 技术栈
- **前端框架**：Vue 3 + TypeScript + Composition API
- **UI 组件库**：Element Plus
- **构建工具**：Vite
- **图表库**：ECharts
- **HTTP 客户端**：Axios
- **状态管理**：Pinia
- **路由**：Vue Router

### 核心页面设计
1. **股票分析页** (`/analyze`)
   - 搜索栏 + 分析模式选择（全面/财务/估值/护城河/管理层）
   - 实时分析进度跟踪
   - 分析结果展示（Tab 切换：综合报告/财务数据/估值分析/护城河/管理层）
   - 图表可视化（历史价格、财务指标趋势、估值对比）
   - 历史分析记录

2. **持仓管理页** (`/portfolio`)
   - 持仓概览卡片（总成本/总市值/总收益/收益率）
   - 持仓列表表格（实时价格、盈亏计算）
   - 买入/卖出表单
   - 交易历史记录
   - 持仓分布饼图

3. **股票筛选页** (`/screen`)
   - 筛选条件表单（ROE/负债率/毛利率/PE/市值/股息率/行业）
   - 筛选结果表格（支持排序、分页）
   - 结果统计卡片
   - 快速分析功能

4. **首页/仪表盘** (`/`)
   - 快速入口（分析/持仓/筛选）
   - 最近分析的股票
   - 持仓概览摘要

### 开发计划

| 子任务 | 状态 | 说明 |
|--------|------|------|
| **Stage 1: 基础框架** | ⏳ 待开始 | |
| 初始化 Vite + Vue 3 + TypeScript 项目 | ⏳ | 创建 `frontend/` 目录 |
| 安装依赖（Element Plus、ECharts、Axios、Pinia、Vue Router） | ⏳ | |
| 配置路由和布局组件（Header、Sidebar、Layout） | ⏳ | |
| 封装 API 客户端（Axios 实例 + 拦截器） | ⏳ | |
| **Stage 2: 持仓管理页面** | ⏳ 待开始 | |
| 持仓概览卡片（调用 `/api/portfolio` 和 `/api/portfolio/performance`） | ⏳ | |
| 持仓列表表格（实时价格刷新） | ⏳ | |
| 买入/卖出表单（调用 `/api/portfolio/buy` 和 `/api/portfolio/sell`） | ⏳ | |
| 交易历史表格（调用 `/api/portfolio/history`） | ⏳ | |
| 持仓分布饼图（ECharts） | ⏳ | |
| **Stage 3: 股票分析页面** | ⏳ 待开始 | |
| 搜索栏和分析模式选择 | ⏳ | |
| 分析进度跟踪（轮询或 WebSocket） | ⏳ | |
| 分析结果展示（Tab 切换、Markdown 渲染） | ⏳ | |
| 图表可视化（历史价格、财务指标、估值对比） | ⏳ | |
| 历史分析记录 | ⏳ | |
| **Stage 4: 股票筛选页面** | ⏳ 待开始 | |
| 筛选条件表单 | ⏳ | |
| 结果表格（调用 `/api/screen`） | ⏳ | |
| 结果统计卡片 | ⏳ | |
| 快速分析功能 | ⏳ | |
| **Stage 5: 优化与部署** | ⏳ 待开始 | |
| 响应式设计（移动端适配） | ⏳ | |
| 错误处理和 Loading 状态 | ⏳ | |
| 构建生产版本（`npm run build`） | ⏳ | |
| 集成到 FastAPI 静态文件服务 | ⏳ | 修改 `server.py` |
| CORS 配置（开发环境） | ⏳ | |

### 后端改动（最小化）
- 在 `server.py` 中添加静态文件挂载（`app.mount("/", StaticFiles(...))`）
- 添加 CORS 中间件（开发环境）
- 可选：WebSocket 支持（实时分析进度推送）

### UI 设计风格
- **配色**：深蓝色（主色）+ 金色（辅助）+ 绿色（盈利）+ 红色（亏损）
- **字体**：思源黑体/苹方（中文）+ Inter/Roboto（英文）
- **组件风格**：圆角卡片、轻微阴影、8px 倍数间距

### 可选增强功能（Phase 5+）
- 实时市场数据（WebSocket 推送）
- 智能提醒（盈亏阈值通知）
- 对比分析（多股票对比）
- 自定义仪表盘
- 暗色模式
- 多语言（中英文切换）
- 导出功能（PDF 报告、Excel 持仓）

---

## 已实现功能清单

### Agent 层（8/8 完成）

| Agent | 文件 | 职责 | 状态 |
|-------|------|------|------|
| BaseAgent | `agents/base.py` | 基类：Claude API tool_use 循环 | ✅ |
| ScreenerAgent | `agents/screener.py` | 按价值投资标准筛选股票 | ✅ |
| MoatAgent | `agents/moat.py` | 护城河分析（品牌、网络效应、转换成本等） | ✅ |
| ManagementAgent | `agents/management.py` | 管理层评估（诚信度、资本配置、股东导向） | ✅ |
| FinancialAgent | `agents/financial.py` | 深度财务分析（FCF、ROE、杜邦分析等） | ✅ |
| ValuationAgent | `agents/valuation.py` | 内在价值估算（DCF、Owner Earnings、安全边际） | ✅ |
| DecisionAgent | `agents/decision.py` | 综合决策（Buy/Hold/Sell） | ✅ |
| PortfolioAgent | `agents/portfolio.py` | 持仓管理（交易记录、收益追踪、AI 回顾） | ✅ |

### 工具层（4/4 完成）

| 工具 | 文件 | 功能 | 状态 |
|------|------|------|------|
| 市场数据 | `tools/market_data.py` | yfinance 封装（股票信息、财报、历史价格） | ✅ |
| 估值计算 | `tools/calculator.py` | DCF、Owner Earnings、安全边际计算 | ✅ |
| 股票筛选 | `tools/screener.py` | S&P 500 筛选（ROE、负债率、毛利率等） | ✅ |
| 持仓管理 | `tools/portfolio.py` | 买入/卖出/查持仓/交易记录/业绩汇总 | ✅ |

### CLI 命令

| 命令 | 用法 | 状态 |
|------|------|------|
| 深度分析 | `moatlab analyze AAPL [-m full/financial/valuation/moat/management]` | ✅ |
| 股票筛选 | `moatlab screen [--roe-min 0.15] [--sector Technology]` | ✅ |
| 持仓管理 | `moatlab portfolio add/sell/list/review/history` | ✅ |
| Web 服务 | `moatlab serve [--port 8000]` | ✅ |

### Web API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/portfolio` | GET | 获取持仓 |
| `/api/portfolio/buy` | POST | 买入 |
| `/api/portfolio/sell` | POST | 卖出 |
| `/api/portfolio/performance` | GET | 业绩汇总 |
| `/api/portfolio/history` | GET | 交易记录 |
| `/api/analyze/{ticker}` | POST | 股票分析 |
| `/api/screen` | POST | 股票筛选 |

---

## 技术栈

| 层次 | 选型 | 版本要求 |
|------|------|---------|
| LLM | Claude API (anthropic SDK) | >= 0.49.0 |
| 市场数据 | yfinance | >= 0.2.40 |
| SEC 财报 | edgartools | >= 3.0.0 |
| CLI | Typer + Rich | >= 0.15.0 |
| Web API | FastAPI + Uvicorn | >= 0.115.0 |
| 数据存储 | SQLite (stdlib) | — |
| 包管理 | uv | — |

---

## 版本记录

| 版本 | 日期 | 里程碑 |
|------|------|--------|
| v0.4.0 | 2026-03 | Phase 4 进行中：Web UI 前端 |
| v0.3.0 | 2026-03 | Phase 3 完成：持仓管理 + Web API |
| v0.2.0 | 2026-03 | Phase 2 完成：完整分析链 + 筛选 |
| v0.1.0 | 2026-03 | Phase 1 完成：单股分析 MVP |
