# MoatLab Lark Bot — 产品功能设计

> 注：使用海外版 Lark（非国内飞书），API 域名为 `open.larksuite.com`，SDK 使用 `lark-oapi`（同时支持 Lark/飞书，通过 `domain` 参数区分）。

## 一、产品定位

Lark Bot 是 MoatLab 的**即时交互入口**，让用户在 Lark 对话中随时触发价值投资分析，无需打开 Web UI 或终端。核心价值：**即时可用、结果直达、团队可见**。

### 目标用户

- 已使用 MoatLab 的个人投资者，希望更便捷地触发分析
- 投资讨论群成员，需要在讨论中快速引用分析结果

### 核心使用场景

| 场景 | 描述 |
|------|------|
| 快速分析 | 私聊或群里 @Bot 发送 ticker，立刻获得投资分析报告 |
| 群内讨论 | 讨论某只股票时 @Bot 分析，结果群内所有人可见 |
| 定时推送 | Bot 每日/每周主动推送持仓盈亏摘要（P2） |

---

## 二、功能范围

### MVP（P0）— 全面分析

Lark Bot MVP 仅支持 **股票全面分析**，不涉及单项分析、筛选、持仓管理等操作。

| 指令 | 示例 | 对应后端调用 | 说明 |
|------|------|-------------|------|
| 全面分析 | `分析 AAPL` 或 `analyze AAPL` | `Orchestrator().analyze("AAPL")` | 护城河+管理层+财务+估值+决策 |
| 帮助 | `帮助` 或 `help` | — | 返回使用说明 |

**指令解析规则：**

- 支持中英文：`分析 AAPL` = `analyze AAPL`
- Ticker 自动大写
- 无法识别的消息 → 返回帮助信息

### 后续迭代

| 阶段 | 功能 |
|------|------|
| P1 | 单项分析（护城河/管理层/财务/估值）、消息卡片格式 |
| P1 | 股票筛选 |
| P2 | 每日持仓推送、分析完成主动通知 |

---

## 三、交互流程

### 3.1 被动响应流程

```
用户在 Lark 发消息（私聊或群聊 @Bot）
  ↓
Lark 开放平台 → POST /lark/webhook（事件回调）
  ↓
MoatLab 解析指令（指令解析器）
  ↓
调用 Orchestrator.analyze(ticker)
  ↓
格式化结果为 Lark 消息格式
  ↓
通过 Lark API 发送回复
```

### 3.2 长任务处理

全面分析耗时 30-60 秒，需要特殊处理：

1. 收到指令后 **立即回复** "正在分析 AAPL，请稍候..."（3 秒内响应，满足 Lark 超时要求）
2. 后台异步执行分析
3. 分析完成后 **主动发送** 结果消息（使用 Lark 发消息 API）

### 3.3 错误处理

| 场景 | 处理 |
|------|------|
| Ticker 不存在 | 返回 "未找到股票 XXX，请检查代码是否正确" |
| 分析超时/失败 | 返回 "分析 XXX 失败，请稍后重试" |
| 无法解析指令 | 返回帮助信息 |
| Lark 验证请求 | 正确响应 URL Verification challenge |

---

## 四、技术方案概要

### 4.1 架构

推荐 **和 FastAPI 集成**，在现有 server 上新增 Lark webhook 路由：

```
Lark 开放平台
  ↓ POST /lark/webhook
MoatLab FastAPI Server
  ├── /api/*            (现有 Web API)
  ├── /lark/webhook     (Lark 事件回调)
  └── 内部调用 agents   (分析)
        ↓ 结果
  Lark API (发消息)  ←── 异步回调
```

**理由：**
- MoatLab 是单用户/小团队工具，无需独立服务的复杂度
- 复用现有 agent 调用逻辑，避免重复代码
- 统一部署和配置管理

### 4.2 Lark 开放平台配置

需要在 [Lark Developer Console](https://open.larksuite.com/) 创建应用：

| 配置项 | 值 |
|--------|-----|
| 应用类型 | Custom App（企业内部） |
| Bot 能力 | Enable Bot |
| 事件订阅 | `im.message.receive_v1`（接收消息） |
| 请求地址 | `https://<公网地址>/lark/webhook` |
| 权限范围 | `im:message`（发消息）、`im:message.receive`（收消息） |

### 4.3 新增环境变量

```
LARK_APP_ID              # Lark App ID
LARK_APP_SECRET          # Lark App Secret
LARK_VERIFICATION_TOKEN  # 事件订阅验证 Token
LARK_ENCRYPT_KEY         # 事件加密 Key（可选）
```

### 4.4 依赖

- `lark-oapi` (>=1.5.0) — Lark/飞书官方 Python SDK，配置 `lark.LARK_DOMAIN` 使用海外域名

---

## 五、消息格式设计

### MVP — 纯文本 / Markdown

Lark 支持 Markdown 子集。分析结果直接以文本消息发送：

**全面分析回复示例：**

```
📊 AAPL 价值投资分析

━━ 投资决策 ━━
建议: 持有
安全边际: 15%（低于目标 30%）
...

━━ 护城河分析 ━━
...

━━ 管理层分析 ━━
...

━━ 财务分析 ━━
...

━━ 估值分析 ━━
...

👉 查看完整报告: http://localhost:5173/analysis?ticker=AAPL
```

**消息长度处理：**
- 全面分析报告可能很长（5000+ 字），Lark 单条消息有长度限制
- 策略：投资决策章节完整展示，其他维度仅展示摘要 + "查看完整报告"链接
- 或拆分为多条消息逐个发送各维度分析

### P1 — 消息卡片

使用 Lark Interactive Card JSON 模板，支持：
- 彩色标题栏（绿色=买入、红色=卖出、灰色=持有）
- 多列布局展示关键指标
- 折叠/展开按钮
- 底部操作按钮（跳转 Web）

---

## 六、实施优先级

| 阶段 | 功能 | 说明 |
|------|------|------|
| **P0** | Lark webhook 接入 + 指令解析 + 全面分析 + 文本回复 | 核心闭环：发 ticker → 收分析报告 |
| **P0** | 长任务异步处理 | 全面分析 30-60s，必须异步 |
| **P0** | 帮助指令 + 错误处理 | 基本可用性 |
| **P1** | 单项分析 + 股票筛选 | 扩展指令集 |
| **P1** | 消息卡片格式 | 提升阅读体验 |
| **P2** | 定时持仓推送 | 需要定时任务框架 |

---

## 七、API 依赖清单

### 复用现有模块

| 功能 | 内部调用 | 状态 |
|------|---------|------|
| 全面分析 | `Orchestrator().analyze(ticker)` | 已有 |

### 需要新增的模块

| 模块 | 说明 |
|------|------|
| `src/moatlab/channels/lark.py` | Lark 渠道核心：webhook 处理、指令解析、消息发送 |
| `src/moatlab/channels/__init__.py` | 渠道模块初始化 |
| Lark webhook 路由 | 在 `server.py` 中注册 `/lark/webhook` |
| Config 扩展 | `config.py` 新增 Lark 相关环境变量 |

### Lark API 调用

| API | 用途 |
|-----|------|
| 发送消息 | 回复分析结果 |
| 回复消息 | 在群聊中 reply 原消息 |
| 获取 tenant_access_token | API 鉴权 |
