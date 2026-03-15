# MoatLab — Feature Log

> 功能迭代日志 — 记录每次交付的新增功能、改进和修复

---

## 格式说明

每条记录格式：
```
### [日期] — [PR#] [标题]
**类型**: feat | fix | refactor | docs | perf | test
**影响范围**: [模块/组件]
**描述**: [简要说明]
**技术细节**: [可选，关键实现要点]
```

---

## 2026-03-16

### [2026-03-16] — #33 股票搜索功能 Phase 2 完成
**类型**: feat
**影响范围**: frontend + backend
**描述**: 完成股票搜索功能增强，新增模糊匹配、搜索历史和热门股票快捷入口
**技术细节**:
- 模糊匹配：使用 `difflib.SequenceMatcher` 计算相似度，阈值 0.6，支持拼写容错
- 搜索历史：localStorage 存储最近 10 条，支持清除
- 热门股票：8 个常用股票快捷入口（AAPL, MSFT, GOOGL 等）
- Enter 键行为优化：仅选择建议，不直接触发分析
- 测试覆盖：26 个单元测试 + 14 个 API 测试，全部通过

### [2026-03-16] — 股票分析进度可视化产品设计
**类型**: docs
**影响范围**: 产品规划
**描述**: 完成股票分析进度可视化功能的产品规格文档
**技术细节**:
- 设计 5 步进度展示 UI（护城河、管理层、财务、估值、综合决策）
- 提出 SSE/WebSocket 实时通信方案
- 定义关键信息提取规则（每步完成后显示 1-2 句摘要）
- 分 3 个阶段实施：P0 基础进度、P1 关键信息、P2 增强交互
- 文档：`docs/analysis-progress-product-spec-2026-03-16.md`

---

## 2026-03-15

### [2026-03-15] — #25 Web UI Stage 4 完成
**类型**: feat
**影响范围**: frontend
**描述**: 完成 Web UI 第四阶段开发，新增分析历史本地缓存功能
**技术细节**:
- 分析历史使用 localStorage 缓存，最多保留 10 条记录
- 仪表盘组件增加防御性处理，应对后端返回缺失字段

### [2026-03-15] — 补充功能迭代工作流文档
**类型**: docs
**影响范围**: 项目文档
**描述**: 在 CONTRIBUTING.md 中补充功能迭代工作流（Product Spec → Tech Design → 分阶段施工）

---

## 2026-03 (Phase 3 完成)

### Phase 3 — 持仓管理 + Web API
**类型**: feat
**影响范围**: 全栈（后端 + API）
**描述**: 完整的持仓管理系统和 RESTful API
**交付内容**:
- SQLite 持久化层 + 数据模型（#8）
- 持仓管理工具函数：买入/卖出/查询/业绩（#9）
- PortfolioAgent + 持仓管理提示词（#10）
- CLI 持仓命令：`moatlab portfolio add/sell/list/review/history`（#11）
- FastAPI Web API + `moatlab serve` 命令（#12）
- 测试覆盖（21 个测试用例）+ 文档更新（#13）

---

## 2026-03 (Phase 2 完成)

### Phase 2 — 完整分析链
**类型**: feat
**影响范围**: Agent 层 + Orchestrator
**描述**: 7 个 Agent 全部就位，Orchestrator 编排完整分析流程
**交付内容**:
- MoatAgent — 护城河分析（#4）
- ManagementAgent — 管理层分析（#5）
- DecisionAgent — 投资决策（#6）
- Orchestrator 编排引擎（并行 + 串行 DAG 调度）（#6）
- 全链路 CLI：`moatlab analyze AAPL`（#6）
- ScreenerAgent + 股票筛选工具（#7）
- CLI 筛选命令：`moatlab screen --roe-min 0.15`（#7）

---

## 2026-03 (Phase 1 完成)

### Phase 1 — 单股分析 CLI (MVP)
**类型**: feat
**影响范围**: 核心架构 + 基础 Agent
**描述**: 跑通单股财务分析 + 估值的最小可用版本
**交付内容**:
- 项目脚手架（pyproject.toml、目录结构、配置管理）（#1）
- BaseAgent 基类 + Claude API tool_use 循环（#2）
- yfinance 市场数据工具封装（#2）
- FinancialAgent + 财务分析提示词（#2）
- DCF/Owner Earnings 计算器（#3）
- ValuationAgent + 估值分析提示词（#3）
- CLI 入口：`moatlab analyze AAPL -m financial/valuation`（#3）

---

## 使用指南

### 新增功能时
1. 在对应日期下添加新条目
2. 填写完整的元信息（类型、影响范围、描述）
3. 如有关键技术细节，补充到"技术细节"字段
4. 关联 PR 编号（如有）

### 维护原则
- 按时间倒序排列（最新在上）
- 每个 PR 合并后立即更新
- 重大功能可单独成节（如 Phase 1/2/3）
- 保持描述简洁，详细内容参考 PR 或技术文档
