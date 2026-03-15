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

SDK 支持两种接收消息的方式：

| 模式 | 适用场景 | 是否需要公网 URL |
|------|---------|----------------|
| **WebSocket 长连接** | 开发/本地测试 | 否，Bot 主动连 Lark 服务器 |
| **HTTP Callback** | 生产部署 | 是，Lark 推送到你的 webhook |

**策略：MVP 用 WebSocket 模式**，无需公网 URL 和内网穿透，开发体验最佳。生产部署时切换为 HTTP Callback。

---

## 二、项目结构

新增模块（不影响现有代码）：

```
src/moatlab/bot/
├── __init__.py
├── lark.py              # Lark Bot 核心：客户端初始化、事件处理、消息发送
├── commands.py          # 指令解析器：文本 → 结构化指令
└── formatter.py         # 结果格式化：分析报告 → Lark 消息格式
```

修改文件：

```
src/moatlab/config.py    # 新增 Lark 环境变量
src/moatlab/server.py    # 新增 /lark/webhook 路由（HTTP Callback 模式）
src/moatlab/cli.py       # 新增 `moatlab lark` 命令（WebSocket 模式）
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

### 4.1 Lark 客户端 (`bot/lark.py`)

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
- 发送/回复消息
- WebSocket 模式启动

**消息事件处理流程：**

```python
def handle_message(data: P2ImMessageReceiveV1) -> None:
    message = data.event.message
    text = extract_text(message.content)  # 解析消息文本
    chat_id = message.chat_id
    message_id = message.message_id

    command = parse_command(text)  # 指令解析

    if command.type == "help":
        reply_text(message_id, HELP_TEXT)
        return

    if command.type == "analyze":
        # 先回复"分析中..."
        reply_text(message_id, f"正在分析 {command.ticker}，请稍候...")
        # 后台异步执行分析
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

### 4.2 指令解析 (`bot/commands.py`)

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

### 4.3 结果格式化 (`bot/formatter.py`)

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

## 五、两种运行模式

### 5.1 WebSocket 模式（开发推荐）

新增 CLI 命令 `moatlab lark`：

```python
# cli.py
@app.command()
def lark():
    """启动 Lark Bot（WebSocket 长连接模式）。"""
    from moatlab.bot.lark import start_ws
    start_ws()
```

实现：

```python
def start_ws():
    """WebSocket 长连接模式 — 无需公网 URL。"""
    event_handler = EventDispatcherHandler.builder(
        settings.lark_encrypt_key,
        settings.lark_verification_token,
    ).register_p2_im_message_receive_v1(handle_message).build()

    ws_client = lark.ws.Client(
        app_id=settings.lark_app_id,
        app_secret=settings.lark_app_secret,
        event_handler=event_handler,
        domain=lark.LARK_DOMAIN,
        log_level=lark.LogLevel.INFO,
    )
    ws_client.start()  # 阻塞运行
```

### 5.2 HTTP Callback 模式（生产部署）

在 `server.py` 新增路由：

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/lark/webhook")
async def lark_webhook(request: Request):
    """Lark 事件回调入口。"""
    body = await request.json()

    # URL Verification
    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    # 事件处理（委托给 event handler）
    from moatlab.bot.lark import handle_event
    return handle_event(body, dict(request.headers))
```

---

## 六、数据流

```
用户发消息 "@MoatLab 分析 AAPL"
  ↓
Lark Platform → WebSocket/HTTP → handle_message()
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
| 5 | 连接方式：选择 WebSocket（开发）或 HTTP Callback（生产） |
| 6 | 发布应用版本 |

---

## 八、实施阶段

### Stage 1: Bot 核心 + WebSocket 模式（P0）

- [ ] `pyproject.toml` 添加 `lark-oapi` 依赖
- [ ] `config.py` 新增 Lark 环境变量
- [ ] `bot/lark.py` — 客户端初始化、事件处理、消息收发
- [ ] `bot/commands.py` — 指令解析（analyze + help）
- [ ] `bot/formatter.py` — 分析结果格式化
- [ ] `cli.py` 新增 `moatlab lark` 命令（WebSocket 启动）
- [ ] 异步分析 + 结果推送
- [ ] 端到端验证：Lark 发 "分析 AAPL" → 收到分析报告

### Stage 2: HTTP Callback + 群聊支持（P0）

- [ ] `server.py` 新增 `/lark/webhook` 路由
- [ ] URL Verification 处理
- [ ] 群聊 @mention 解析（去除 @Bot 前缀提取指令）
- [ ] 群聊用 reply（关联原消息），私聊用 send

### Stage 3: 消息卡片 + 扩展指令（P1）

- [ ] Interactive Card 模板（买入/卖出/持有 配色）
- [ ] 单项分析指令（护城河/管理层/财务/估值）
- [ ] 股票筛选指令
