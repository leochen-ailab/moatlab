# MoatLab Lark Bot — 技术方案概要

> 对应产品文档：`docs/lark-bot-product-spec.md`

---

## 一、技术选型

| 层次 | 选型 | 版本 | 理由 |
|------|------|------|------|
| Lark SDK | lark-oapi | >=1.5.0 | 官方 Python SDK，支持 Lark/飞书双域名 |
| Web 框架 | FastAPI（现有） | >=0.115.0 | 复用现有 server，新增 webhook 路由 |
| 异步 | asyncio + threading | — | 长任务后台执行，避免 webhook 超时 |

### 连接模式

使用 **HTTP Callback**（将事件发送至开发者服务器）：Lark 平台将消息事件 POST 到 MoatLab 的 `/lark/webhook` 端点，集成到现有 FastAPI server。需要服务器有公网可达的 URL。

---

## 二、项目结构

新增模块（不影响现有代码）：

```
src/moatlab/channels/
├── __init__.py
├── lark.py              # Lark 渠道核心：客户端初始化、事件处理、消息发送
├── commands.py          # 指令解析器：文本 → 结构化指令（各渠道共用）
└── formatter.py         # 结果格式化：分析报告 → 消息文本（各渠道共用）
```

修改文件：

```
src/moatlab/config.py    # 新增 Lark 环境变量
src/moatlab/server.py    # 新增 /lark/webhook 路由
pyproject.toml           # 新增 lark-oapi 依赖
```

---

## 三、配置扩展

### config.py 新增字段

```python
# Lark Bot
lark_app_id: str = field(
    default_factory=lambda: os.environ.get("LARK_APP_ID", "")
)
lark_app_secret: str = field(
    default_factory=lambda: os.environ.get("LARK_APP_SECRET", "")
)
lark_verification_token: str = field(
    default_factory=lambda: os.environ.get("LARK_VERIFICATION_TOKEN", "")
)
lark_encrypt_key: str = field(
    default_factory=lambda: os.environ.get("LARK_ENCRYPT_KEY", "")
)
```

---

## 四、核心模块设计

### 4.1 Lark 客户端 (`channels/lark.py`)

```python
import lark_oapi as lark

# 初始化客户端（海外 Lark 域名）
client = lark.Client.builder() \
    .app_id(settings.lark_app_id) \
    .app_secret(settings.lark_app_secret) \
    .domain(lark.LARK_DOMAIN) \
    .build()
```

**核心职责：**
- 初始化 Lark Client（海外域名）
- 注册消息事件处理器（`im.message.receive_v1`）
- 处理 HTTP Callback 事件
- 发送/回复消息

**消息事件处理流程：**

```python
def handle_message(event: dict) -> None:
    message = event["message"]
    chat_type = message["chat_type"]  # "p2p" | "group"
    text = extract_text(message["content"])
    chat_id = message["chat_id"]
    message_id = message["message_id"]

    # 群聊：需要 @Bot 才触发，去除 @mention 前缀
    # 私聊：直接触发
    if chat_type == "group":
        mentions = message.get("mentions", [])
        if not is_bot_mentioned(mentions):
            return  # 群聊未 @Bot，忽略
        text = strip_mentions(text)  # 去除 @Bot 文本

    command = parse_command(text)

    if command.type == "help":
        reply_text(message_id, HELP_TEXT)
        return

    if command.type == "analyze":
        reply_text(message_id, f"正在分析 {command.ticker}，请稍候...")
        threading.Thread(
            target=run_analysis,
            args=(command.ticker, chat_id),
            daemon=True,
        ).start()
        return

    reply_text(message_id, HELP_TEXT)  # 无法识别 → 帮助
```

**发送消息：**

```python
def send_message(chat_id: str, text: str) -> None:
    """主动发消息到会话（用于异步结果推送）。"""
    request = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()) \
        .build()
    client.im.v1.message.create(request)

def reply_text(message_id: str, text: str) -> None:
    """回复某条消息（群聊中关联上下文）。"""
    request = ReplyMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(ReplyMessageRequestBody.builder()
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()) \
        .build()
    client.im.v1.message.reply(request)
```

### 4.2 指令解析 (`channels/commands.py`)

```python
@dataclass
class Command:
    type: str          # "analyze" | "help" | "unknown"
    ticker: str = ""

def parse_command(text: str) -> Command:
    """解析用户消息为结构化指令。"""
    text = text.strip()

    # 帮助
    if text in ("帮助", "help", "/help"):
        return Command(type="help")

    # 分析: "分析 AAPL" / "analyze AAPL"
    match = re.match(r"(?:分析|analyze)\s+([A-Za-z]{1,5})", text, re.IGNORECASE)
    if match:
        return Command(type="analyze", ticker=match.group(1).upper())

    return Command(type="unknown")
```

### 4.3 结果格式化 (`channels/formatter.py`)

```python
def format_analysis(ticker: str, reports: dict[str, str]) -> str:
    """将 Orchestrator 分析结果格式化为 Lark 消息文本。"""
    sections = [
        ("投资决策", reports.get("decision", "")),
        ("护城河分析", reports.get("moat", "")),
        ("管理层分析", reports.get("management", "")),
        ("财务分析", reports.get("financial", "")),
        ("估值分析", reports.get("valuation", "")),
    ]

    lines = [f"📊 {ticker} 价值投资分析\n"]
    for title, content in sections:
        lines.append(f"━━ {title} ━━")
        lines.append(truncate(content, max_chars=800))
        lines.append("")

    return "\n".join(lines)
```

**消息长度策略：**
- Lark 单条文本消息限制约 30,000 字符
- 全面分析报告通常 3000-8000 字，大部分情况可完整展示
- 超长时截断各章节至 800 字 + 省略提示

### 4.4 异步分析执行

```python
def run_analysis(ticker: str, chat_id: str) -> None:
    """后台线程执行全面分析并推送结果。"""
    try:
        from moatlab.agents.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        reports = orchestrator.analyze(ticker)
        text = format_analysis(ticker, reports)
        send_message(chat_id, text)
    except Exception as e:
        send_message(chat_id, f"分析 {ticker} 失败: {e}")
```

---

## 五、HTTP Callback 接入

在 `server.py` 新增 webhook 路由，处理 Lark 平台推送的事件：

```python
from fastapi import Request

@app.post("/lark/webhook")
async def lark_webhook(request: Request):
    """Lark 事件回调入口（HTTP Callback 模式）。"""
    body = await request.json()

    # URL Verification — Lark 配置 webhook 时的验证请求
    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    # 消息事件处理
    from moatlab.channels.lark import handle_event
    return handle_event(body)
```

`handle_event` 负责解析事件体、验证签名、分发到 `handle_message`：

```python
def handle_event(body: dict) -> dict:
    """解析 Lark 事件并分发处理。"""
    # 提取事件头和消息体
    header = body.get("header", {})
    event = body.get("event", {})
    event_type = header.get("event_type")

    if event_type == "im.message.receive_v1":
        handle_message(event)

    return {"code": 0}  # 告知 Lark 已收到
```

---

## 六、数据流

```
用户发消息 "@MoatLab 分析 AAPL"
  ↓
Lark Platform → POST /lark/webhook → handle_message()
  ↓
parse_command("分析 AAPL") → Command(type="analyze", ticker="AAPL")
  ↓
reply_text("正在分析 AAPL，请稍候...")  ← 立即响应
  ↓
threading.Thread → run_analysis("AAPL", chat_id)
  ↓
Orchestrator().analyze("AAPL")  ← 30-60s
  ↓
format_analysis("AAPL", reports)
  ↓
send_message(chat_id, formatted_text)  ← 推送结果
```

---

## 七、Lark 开放平台配置清单

在 [Lark Developer Console](https://open.larksuite.com/) 完成以下配置：

| 步骤 | 操作 |
|------|------|
| 1 | 创建 Custom App |
| 2 | 添加 Bot 能力 |
| 3 | 权限申请：`im:message`、`im:message.receive` |
| 4 | 事件订阅：`im.message.receive_v1` |
| 5 | 连接方式：选择「将事件发送至开发者服务器」，填入 `https://<公网地址>/lark/webhook` |
| 6 | 发布应用版本 |

---

## 八、实施阶段

### Stage 1: Bot 核心 + HTTP Callback（P0）✅

- [x] `pyproject.toml` 添加 `lark-oapi` 依赖
- [x] `config.py` 新增 Lark 环境变量
- [x] `channels/lark.py` — 客户端初始化、事件处理、消息收发
- [x] `channels/commands.py` — 指令解析（analyze + help），支持模糊匹配和公司名映射
- [x] `channels/formatter.py` — 分析结果格式化
- [x] `server.py` 新增 `/lark/webhook` 路由 + URL Verification
- [x] 私聊直接触发、群聊 @Bot 触发（@mention 解析 + 去前缀）
- [x] 异步分析 + 结果推送

### Stage 2: 消息卡片 + 扩展指令（P1）

- [ ] Interactive Card 模板（买入/卖出/持有 配色）
- [ ] 单项分析指令（护城河/管理层/财务/估值）
- [ ] 股票筛选指令
