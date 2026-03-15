# MoatLab Web UI — 技术方案概要

> 对应产品文档：`docs/web-ui-product-spec.md`

---

## 一、技术选型

| 层次 | 选型 | 版本 | 理由 |
|------|------|------|------|
| 构建工具 | Vite | 6.x | 快速 HMR，React 生态标配 |
| 框架 | React + TypeScript | 19.x / 5.x | ARCHITECTURE.md 指定 |
| 样式 | TailwindCSS | 4.x | ARCHITECTURE.md 指定，utility-first |
| 路由 | React Router | 7.x | SPA 客户端路由 |
| 状态管理 | Zustand | 5.x | 轻量无样板，适合中小应用 |
| Markdown 渲染 | react-markdown + remark-gfm | — | 分析报告均为 markdown |
| 图表 | Recharts | 2.x | 仪表盘饼图，React 原生 |
| HTTP | 原生 fetch | — | API 简单，无需引入 axios |

不引入 UI 组件库（shadcn/antd），用 TailwindCSS 手写，保持轻量。

---

## 二、项目结构

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts              # proxy /api → localhost:8000
├── src/
│   ├── main.tsx                # ReactDOM 入口
│   ├── App.tsx                 # Router + Layout
│   ├── index.css               # TailwindCSS 入口
│   │
│   ├── types/                  # TS 类型定义（对齐后端 Pydantic）
│   │   ├── portfolio.ts        # Position, Trade, Performance
│   │   ├── analysis.ts         # AnalysisRequest, AnalysisResult
│   │   └── screener.ts         # ScreenRequest, ScreenResult
│   │
│   ├── api/                    # API 客户端（一个文件一个领域）
│   │   ├── client.ts           # fetch 封装：baseURL、错误处理、JSON 解析
│   │   ├── portfolio.ts        # getPortfolio, buy, sell, getPerformance, getHistory
│   │   ├── analysis.ts         # analyze(ticker, mode)
│   │   └── screener.ts         # screen(criteria)
│   │
│   ├── stores/                 # Zustand stores
│   │   ├── portfolioStore.ts   # 持仓数据（全局共享）
│   │   ├── analysisStore.ts    # 分析结果（页面级）
│   │   └── screenerStore.ts    # 筛选结果（页面级）
│   │
│   ├── pages/                  # 页面组件（路由级）
│   │   ├── DashboardPage.tsx
│   │   ├── PortfolioPage.tsx
│   │   ├── AnalysisPage.tsx
│   │   └── ScreenerPage.tsx
│   │
│   └── components/             # 业务组件
│       ├── layout/
│       │   └── AppLayout.tsx   # 顶部导航 + 内容区
│       ├── portfolio/
│       │   ├── PositionTable.tsx
│       │   ├── TradeDrawer.tsx
│       │   ├── PortfolioSummary.tsx
│       │   ├── AllocationChart.tsx
│       │   └── TransactionHistory.tsx
│       ├── analysis/
│       │   ├── AnalysisSearch.tsx
│       │   └── AnalysisReport.tsx
│       ├── screener/
│       │   ├── ScreenerForm.tsx
│       │   └── ScreenerResults.tsx
│       └── common/
│           ├── Spinner.tsx
│           └── Toast.tsx
```

---

## 三、路由设计

```tsx
// App.tsx
<Routes>
  <Route element={<AppLayout />}>
    <Route path="/" element={<DashboardPage />} />
    <Route path="/portfolio" element={<PortfolioPage />} />
    <Route path="/analysis" element={<AnalysisPage />} />
    <Route path="/screener" element={<ScreenerPage />} />
  </Route>
</Routes>
```

`AppLayout` 包含顶部导航栏（NavLink 高亮）+ `<Outlet />` 内容区。

---

## 四、API 客户端设计

### 4.1 fetch 封装 (`api/client.ts`)

```ts
const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};
```

### 4.2 Vite 代理配置

```ts
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

开发时前端 `npm run dev`（5173）+ 后端 `moatlab serve`（8000），通过 Vite proxy 避免 CORS。

---

## 五、状态管理设计

### 5.1 portfolioStore（全局）

仪表盘和持仓页共享，避免重复请求。

```ts
interface PortfolioStore {
  positions: Position[];
  summary: { totalCost: number; totalValue: number; totalReturn: number; totalReturnPct: number };
  performance: Performance | null;
  loading: boolean;
  error: string | null;

  fetchPortfolio: () => Promise<void>;
  fetchPerformance: () => Promise<void>;
  buy: (req: TradeRequest) => Promise<void>;
  sell: (req: TradeRequest) => Promise<void>;
}
```

### 5.2 analysisStore（页面级）

```ts
interface AnalysisStore {
  ticker: string;
  mode: AnalysisMode;
  result: Record<string, string> | null;  // 全面分析: { moat, management, ... }
  loading: boolean;
  error: string | null;

  setTicker: (t: string) => void;
  setMode: (m: AnalysisMode) => void;
  analyze: () => Promise<void>;
  clear: () => void;
}
```

### 5.3 screenerStore（页面级）

```ts
interface ScreenerStore {
  criteria: ScreenCriteria;
  result: string | null;  // markdown
  loading: boolean;
  error: string | null;

  setCriteria: (c: Partial<ScreenCriteria>) => void;
  screen: () => Promise<void>;
}
```

---

## 六、页面 → 组件 → API 映射

### 6.1 仪表盘 (DashboardPage)

```
DashboardPage
├── PortfolioSummary          ← portfolioStore.summary
├── AllocationChart           ← portfolioStore.positions (PieChart)
├── TopMovers                 ← portfolioStore.performance
└── QuickActions              ← navigate(/analysis), TradeDrawer
```

- `useEffect` 加载时调 `fetchPortfolio()` + `fetchPerformance()`
- 饼图点击 → `navigate(/analysis?ticker=XXX)`

### 6.2 持仓管理 (PortfolioPage)

```
PortfolioPage
├── Tabs: [当前持仓 | 交易历史 | 持仓回顾]
│
├── Tab 1: 当前持仓
│   ├── PortfolioSummary      ← portfolioStore.summary
│   ├── PositionTable         ← portfolioStore.positions
│   └── TradeDrawer           ← portfolioStore.buy / sell
│
├── Tab 2: 交易历史
│   └── TransactionHistory    ← GET /api/portfolio/history (本地 state)
│
└── Tab 3: 持仓回顾
    └── ReviewReport          ← POST /api/portfolio/review (本地 state)
```

- Tab 切换用 URL search param `?tab=history` 保持可分享
- TradeDrawer 提交成功后自动 `fetchPortfolio()` 刷新表格

### 6.3 股票分析 (AnalysisPage)

```
AnalysisPage
├── AnalysisSearch            ← analysisStore.setTicker / setMode
└── AnalysisReport            ← analysisStore.result
    ├── 全面模式: CollapsibleSection × 5
    └── 单项模式: Markdown 直接渲染
```

- URL query `?ticker=AAPL` 支持从其他页面跳转预填
- 全面分析结果为 `{ moat, management, financial, valuation, decision }`，按 key 分 Section 渲染

### 6.4 股票筛选 (ScreenerPage)

```
ScreenerPage
├── ScreenerForm              ← screenerStore.setCriteria
└── ScreenerResults           ← screenerStore.result (Markdown)
```

- 结果中的 ticker 文本匹配后渲染为可点击链接 → `/analysis?ticker=XXX`

---

## 七、后端需新增的 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/portfolio/review` | POST | 调用 PortfolioAgent 执行持仓回顾，返回 `{ result: "markdown" }` |

实现方式：参考 `cli.py` 中 `portfolio_review` 命令，在 `server.py` 中新增端点。

---

## 八、实施阶段

基于产品优先级，分 4 个阶段交付：

### Stage 1: 项目骨架 ✅ (f6ef441)

- [x] Vite + React + TS + TailwindCSS 初始化
- [x] AppLayout（导航栏 + 路由）
- [x] API client 封装
- [x] TS 类型定义
- [x] Spinner / Toast 通用组件

### Stage 2: 持仓管理 + 股票分析（P0）✅ (b1c2529)

- [x] portfolioStore + analysisStore
- [x] PositionTable + TradeDrawer + PortfolioSummary
- [x] AnalysisSearch + AnalysisReport（含 Markdown 渲染、折叠展开）
- [x] 联调验证：买入 → 表格刷新 → 分析 → 报告渲染

### Stage 3: 仪表盘 + 股票筛选（P1）✅

- [x] DashboardPage：汇总卡片 + 饼图 + 赢家输家 + 快捷入口
- [x] screenerStore + ScreenerForm + ScreenerResults
- [x] 交易历史 Tab（PortfolioPage 增加 Tab 切换）

### Stage 4: 持仓回顾 + 优化（P2）

- 后端新增 `/api/portfolio/review`
- 持仓回顾 Tab
- 深色/浅色主题
- 分析历史本地缓存（localStorage）
