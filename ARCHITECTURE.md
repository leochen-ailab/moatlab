# MoatLab — 巴菲特/段永平价值投资 Agent 系统架构

## Context

构建一个基于巴菲特和段永平价值投资哲学的个人投资系统。项目名 "MoatLab"（护城河实验室）体现了核心理念：寻找具有持久竞争优势的伟大企业。系统以美股为主，采用多 Agent 架构，通过 Claude API 驱动智能分析，覆盖从股票筛选到持仓管理的完整投资流程。

---

## 一、核心投资哲学 → Agent 映射

| 投资原则 | 对应 Agent | 职责 |
|---------|-----------|------|
| 护城河 (Moat) | MoatAgent | 分析品牌、网络效应、转换成本、成本优势、无形资产 |
| 管理层 (Management) | ManagementAgent | 评估管理层诚信度、资本配置能力、股东利益导向 |
| 财务健康 (Financials) | FinancialAgent | 深度财务分析：FCF、ROE、负债率、利润率趋势 |
| 安全边际 (Margin of Safety) | ValuationAgent | 内在价值计算、DCF、Owner Earnings、安全边际评估 |
| 能力圈 (Circle of Competence) | ScreenerAgent | 筛选可理解的、符合能力圈的企业 |
| 买卖决策 (Decision) | DecisionAgent | 综合所有分析，给出 Buy/Hold/Sell 建议 |
| 持仓管理 (Portfolio) | PortfolioAgent | 跟踪持仓、仓位管理、定期回顾 |

---

## 二、系统架构总览

```
┌─────────────────────────────────────────────────────┐
│                   用户交互层                          │
│         CLI (Click/Typer)  ←→  Web UI (FastAPI)      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Orchestrator (编排引擎)                   │
│  接收用户意图 → 拆解任务 → 调度 Agent → 汇总结果       │
└──┬───────┬───────┬───────┬───────┬───────┬───────┬──┘
   │       │       │       │       │       │       │
   ▼       ▼       ▼       ▼       ▼       ▼       ▼
┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐
│Scre-││Moat ││Mgmt ││Fin  ││Valu-││Deci-││Port-│
│ener ││Agent││Agent││Agent││ation││sion ││folio│
│Agent││     ││     ││     ││Agent││Agent││Agent│
└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘
   │       │       │       │       │       │       │
┌──▼───────▼───────▼───────▼───────▼───────▼───────▼──┐
│                    工具层 (Tools)                      │
│  yfinance │ edgartools │ 新闻API │ 计算引擎 │ DB      │
└─────────────────────────────────────────────────────┘
```

---

## 三、Agent 详细设计

### 1. Orchestrator（编排引擎）
- **职责**：理解用户意图，将任务拆解并分发给专业 Agent，汇总最终结果
- **模式**：DAG（有向无环图）编排 — 支持并行执行独立 Agent，串行执行有依赖关系的 Agent
- **实现**：基于 Claude API 的 tool_use，Orchestrator 本身是一个 Claude 对话，其 tools 就是各个子 Agent

### 2. ScreenerAgent（筛选 Agent）
- **输入**：筛选条件（行业、市值范围、ROE 阈值等）
- **输出**：候选股票列表 + 初步评分
- **工具**：yfinance（批量筛选）、自定义筛选规则引擎
- **巴菲特原则**：排除看不懂的行业，优先稳定商业模式

### 3. MoatAgent（护城河分析 Agent）
- **输入**：股票代码
- **输出**：护城河评估报告（类型、强度、持久性评分 1-10）
- **工具**：edgartools（10-K 年报分析）、新闻搜索
- **分析维度**：
  - 品牌价值 (Brand)
  - 网络效应 (Network Effects)
  - 转换成本 (Switching Costs)
  - 成本优势 (Cost Advantages)
  - 规模经济 (Economies of Scale)

### 4. ManagementAgent（管理层分析 Agent）
- **输入**：股票代码
- **输出**：管理层评估报告（诚信度、能力、股东导向评分）
- **工具**：edgartools（Proxy Statement/DEF 14A）、insider trading 数据
- **分析维度**：
  - 管理层持股比例及变动
  - 薪酬合理性
  - 资本配置历史（回购/分红/并购）
  - 段永平强调的"做对的事情"：管理层是否诚实可靠

### 5. FinancialAgent（财务分析 Agent）
- **输入**：股票代码
- **输出**：财务健康报告 + 关键指标趋势
- **工具**：edgartools（10-K/10-Q 解析）、yfinance（历史数据）
- **分析维度**：
  - 自由现金流 (FCF) 及增长趋势
  - ROE/ROIC 及杜邦分析
  - 负债率及利息覆盖
  - 毛利率/净利率变化
  - Owner Earnings（巴菲特式盈利计算）

### 6. ValuationAgent（估值 Agent）
- **输入**：股票代码 + FinancialAgent 的输出
- **输出**：内在价值估算 + 安全边际百分比
- **工具**：自定义 DCF 计算器、yfinance（当前价格）
- **估值方法**：
  - DCF（自由现金流折现）
  - Owner Earnings 估值
  - PE/PB 历史区间对比
  - 安全边际计算（目标 ≥ 30%）

### 7. DecisionAgent（决策 Agent）
- **输入**：以上所有 Agent 的分析报告
- **输出**：Buy / Hold / Sell 建议 + 理由 + 建议仓位
- **原则**：
  - 必须同时满足：好生意 + 好管理 + 好价格
  - "不懂不做"：对不确定的分析明确标注
  - 逆向思考：列出可能出错的理由（段永平的"反过来想"）

### 8. PortfolioAgent（持仓管理 Agent）
- **输入**：当前持仓数据
- **输出**：持仓回顾报告、再平衡建议
- **工具**：本地 SQLite 数据库、yfinance（实时价格）
- **功能**：
  - 持仓记录与收益追踪
  - 定期检查投资逻辑是否仍然成立
  - 集中持仓提醒（巴菲特风格：不超过 10-15 只）

---

## 四、技术栈

| 层次 | 技术选型 | 说明 |
|------|---------|------|
| LLM | Claude API (anthropic SDK) | tool_use 驱动 Agent，模型 claude-sonnet-4-6（性价比）/ claude-opus-4-6（深度分析）|
| 市场数据 | yfinance | 免费，无需 API Key，覆盖美股行情和基本面 |
| SEC 财报 | edgartools | 免费，直接解析 XBRL，支持 10-K/10-Q/DEF14A |
| 数据存储 | SQLite | 轻量，单文件，适合个人系统 |
| CLI | Typer | 现代 Python CLI 框架，自动生成帮助文档 |
| Web API | FastAPI | 异步高性能，自动生成 OpenAPI 文档 |
| Web UI | React + TailwindCSS | 后续迭代（第一期先做 CLI） |
| 包管理 | uv | 快速的 Python 包管理器 |

---

## 五、项目结构

```
moatlab/
├── pyproject.toml              # 项目配置 (uv)
├── src/
│   └── moatlab/
│       ├── __init__.py
│       ├── cli.py              # CLI 入口 (Typer)
│       ├── server.py           # Web API 入口 (FastAPI)
│       ├── config.py           # 配置管理
│       │
│       ├── agents/             # Agent 层
│       │   ├── __init__.py
│       │   ├── base.py         # BaseAgent 基类（统一的 Claude API 调用模式）
│       │   ├── orchestrator.py # 编排引擎
│       │   ├── screener.py     # 筛选 Agent
│       │   ├── moat.py         # 护城河分析 Agent
│       │   ├── management.py   # 管理层分析 Agent
│       │   ├── financial.py    # 财务分析 Agent
│       │   ├── valuation.py    # 估值 Agent
│       │   ├── decision.py     # 决策 Agent
│       │   └── portfolio.py    # 持仓管理 Agent
│       │
│       ├── tools/              # 工具层（Agent 可调用的工具函数）
│       │   ├── __init__.py
│       │   ├── market_data.py  # yfinance 封装
│       │   ├── sec_filings.py  # edgartools 封装
│       │   ├── calculator.py   # DCF/估值计算器
│       │   └── news.py         # 新闻搜索
│       │
│       ├── models/             # 数据模型
│       │   ├── __init__.py
│       │   ├── stock.py        # 股票数据模型
│       │   ├── report.py       # 分析报告模型
│       │   └── portfolio.py    # 持仓数据模型
│       │
│       └── store/              # 持久化层
│           ├── __init__.py
│           └── database.py     # SQLite 操作
│
├── prompts/                    # Agent 系统提示词（独立管理，方便迭代）
│   ├── screener.md
│   ├── moat.md
│   ├── management.md
│   ├── financial.md
│   ├── valuation.md
│   ├── decision.md
│   └── portfolio.md
│
└── tests/
    ├── test_agents/
    └── test_tools/
```

---

## 六、Agent 核心实现模式

每个 Agent 的工作模式统一为 **Claude API tool_use 循环**：

```python
# 伪代码示意
class BaseAgent:
    def __init__(self, name, system_prompt, tools):
        self.client = Anthropic()
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools  # Claude API tool definitions

    async def run(self, user_input: str) -> AgentResult:
        messages = [{"role": "user", "content": user_input}]

        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
                max_tokens=4096,
            )

            if response.stop_reason == "end_turn":
                return self.parse_result(response)

            # 处理 tool_use 请求
            for block in response.content:
                if block.type == "tool_use":
                    result = await self.execute_tool(block.name, block.input)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": block.id, "content": result}]
                    })
```

Orchestrator 将每个子 Agent 注册为自己的 tool，实现嵌套调用：

```python
# Orchestrator 的 tools 就是各个子 Agent
orchestrator_tools = [
    {"name": "screen_stocks", "description": "筛选符合价值投资标准的股票"},
    {"name": "analyze_moat", "description": "分析公司护城河"},
    {"name": "analyze_management", "description": "评估管理层质量"},
    {"name": "analyze_financials", "description": "深度财务分析"},
    {"name": "calculate_valuation", "description": "计算内在价值和安全边际"},
    {"name": "make_decision", "description": "综合分析给出投资建议"},
    {"name": "manage_portfolio", "description": "管理投资组合"},
]
```

---

## 七、典型工作流示例

**用户输入**: `analyze AAPL`（深度分析苹果公司）

```
Orchestrator 接收 "analyze AAPL"
  ├── 并行执行:
  │   ├── MoatAgent("AAPL")      → 护城河报告
  │   ├── ManagementAgent("AAPL") → 管理层报告
  │   └── FinancialAgent("AAPL")  → 财务报告
  │
  ├── 串行执行（依赖财务数据）:
  │   └── ValuationAgent("AAPL", financial_data) → 估值报告
  │
  └── 最终汇总:
      └── DecisionAgent(all_reports) → 投资建议
```

---

## 八、分期实施路线

### Phase 1（MVP）— 单股分析 CLI ⬅️ 当前阶段
- BaseAgent 基类 + Claude API tool_use 循环
- FinancialAgent + ValuationAgent（先跑通财务分析 + 估值）
- yfinance + edgartools 工具封装
- CLI 入口：`moatlab analyze AAPL`

### Phase 2 — 完整分析链
- MoatAgent + ManagementAgent + DecisionAgent
- Orchestrator 编排引擎
- 提示词精调
- `moatlab screen --roe-min 15 --debt-ratio-max 0.5`

### Phase 3 — 持仓管理 + Web UI
- PortfolioAgent + SQLite 持久化
- FastAPI Web API
- React 前端
- `moatlab portfolio add AAPL --shares 100 --price 150`

---

## 九、验证方式

1. **单元测试**：各 Agent 的工具函数独立测试（yfinance 数据获取、DCF 计算等）
2. **集成测试**：选取已知公司（如 AAPL、KO）运行完整分析流程，对比人工分析结果
3. **CLI 端到端**：`moatlab analyze AAPL` 应输出完整的价值投资分析报告
4. **基准对比**：用巴菲特已知的持仓（BRK 重仓股）验证系统评分是否合理
