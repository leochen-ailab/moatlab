# Tech Design: 股票搜索功能实现

## Overview

本文档描述股票搜索功能的技术实现方案，对应产品规格：`stock-search-product-spec-2026-03-15.md`

## Architecture

### System Components

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  Data Layer │
│             │      │   API        │      │             │
│ - Search UI │      │ - /api/search│      │ - yfinance  │
│ - Autocomplete     │ - Fuzzy match│      │ - Local DB  │
│ - History   │      │ - Cache      │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
```

## API Design

### Endpoint: `GET /api/search/stocks`

**Query Parameters:**
- `q` (required): 搜索关键词
- `limit` (optional): 返回结果数量，默认 10

**Response:**
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "name_cn": "苹果公司",
      "sector": "Technology",
      "exchange": "NASDAQ",
      "match_score": 1.0
    }
  ],
  "query": "苹果",
  "total": 1
}
```

**Error Response:**
```json
{
  "error": "Invalid query",
  "message": "Query must be at least 1 character"
}
```

## Backend Implementation

### Phase 1: MVP

**文件结构：**
```
src/moatlab/
├── tools/
│   └── stock_search.py          # 搜索核心逻辑
├── data/
│   └── company_mappings.py      # 公司名映射数据
└── server.py                    # API 路由
```

**核心逻辑：**

1. **复用现有映射**
   - 从 `channels/commands.py` 提取 `_COMPANY_TO_TICKER` 映射
   - 移到独立的 `data/company_mappings.py` 模块
   - 支持中英文公司名查询

2. **搜索算法（简单版）**
   ```python
   def search_stocks(query: str, limit: int = 10) -> list[dict]:
       query_lower = query.lower().strip()
       results = []

       # 1. 精确匹配 ticker
       if is_valid_ticker(query_lower):
           results.append(get_stock_info(query.upper()))

       # 2. 公司名映射匹配
       if query_lower in COMPANY_TO_TICKER:
           ticker = COMPANY_TO_TICKER[query_lower]
           results.append(get_stock_info(ticker))

       # 3. 部分匹配（子串）
       for name, ticker in COMPANY_TO_TICKER.items():
           if query_lower in name:
               results.append(get_stock_info(ticker))

       return deduplicate(results)[:limit]
   ```

3. **数据获取**
   - 复用 `tools/market_data.py` 的 `get_stock_info()`
   - 返回 ticker、公司名、行业、交易所

### Phase 2: 增强搜索

**模糊匹配：**
- 使用 `difflib.SequenceMatcher` 或 `fuzzywuzzy` 库
- 计算查询词与公司名的相似度分数
- 按相似度排序结果

```python
from difflib import SequenceMatcher

def fuzzy_search(query: str, candidates: dict) -> list[tuple[str, float]]:
    scores = []
    for name, ticker in candidates.items():
        ratio = SequenceMatcher(None, query.lower(), name).ratio()
        if ratio > 0.6:  # 阈值
            scores.append((ticker, ratio))
    return sorted(scores, key=lambda x: x[1], reverse=True)
```

**缓存策略：**
- 使用 `functools.lru_cache` 缓存搜索结果
- 缓存 TTL: 1 小时
- 热门查询优先缓存

### Phase 3: 数据源扩展

**选项 1: 本地数据库**
- 构建 SQLite 数据库存储 ticker 元数据
- 表结构：
  ```sql
  CREATE TABLE stocks (
    ticker TEXT PRIMARY KEY,
    name TEXT,
    name_cn TEXT,
    sector TEXT,
    exchange TEXT,
    market_cap REAL,
    aliases TEXT  -- JSON array of alternative names
  );
  ```
- 初始数据：S&P 500 + 常见中概股（约 600 条）

**选项 2: 第三方 API**
- Alpha Vantage: `SYMBOL_SEARCH` endpoint
- Polygon.io: `/v3/reference/tickers`
- 优点：数据全面、实时更新
- 缺点：API 限流、成本

**推荐：** 混合方案
- 本地数据库作为主要数据源（快速、免费）
- 第三方 API 作为补充（处理未知 ticker）

## Frontend Implementation

### Component Structure

```
frontend/src/
├── components/
│   └── analysis/
│       ├── AnalysisSearch.tsx       # 现有组件（修改）
│       └── StockSearchDropdown.tsx  # 新增：搜索建议下拉
├── hooks/
│   └── useStockSearch.ts            # 新增：搜索逻辑 hook
├── api/
│   └── search.ts                    # 新增：搜索 API 客户端
└── utils/
    └── searchHistory.ts             # 新增：搜索历史管理
```

### Key Components

**1. StockSearchDropdown.tsx**
```tsx
interface SearchResult {
  ticker: string;
  name: string;
  name_cn?: string;
  sector: string;
}

interface Props {
  query: string;
  results: SearchResult[];
  loading: boolean;
  onSelect: (ticker: string) => void;
}

// 功能：
// - 显示搜索结果列表
// - 键盘导航（ArrowUp/Down, Enter）
// - 高亮匹配文本
// - 空状态提示
```

**2. useStockSearch Hook**
```tsx
function useStockSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.length >= 2) {
        searchStocks(query);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  return { query, setQuery, results, loading };
}
```

**3. Search History**
```typescript
// localStorage key: 'moatlab_search_history'
interface HistoryItem {
  ticker: string;
  name: string;
  timestamp: number;
}

function addToHistory(item: HistoryItem): void;
function getHistory(limit: number = 10): HistoryItem[];
function clearHistory(): void;
```

## Data Management

### Company Mappings

**数据来源：**
1. 现有 Lark Bot 映射（80+ 条）
2. 手动补充常见股票
3. 用户反馈补充

**数据格式：**
```python
# data/company_mappings.py
COMPANY_TO_TICKER = {
    # 中文名
    "苹果": "AAPL",
    "苹果公司": "AAPL",
    # 英文名
    "apple": "AAPL",
    "apple inc": "AAPL",
    # 别名
    "元宇宙": "META",
    "脸书": "META",
}

# 反向索引（ticker -> 公司信息）
TICKER_INFO = {
    "AAPL": {
        "name": "Apple Inc.",
        "name_cn": "苹果公司",
        "aliases": ["苹果", "apple"],
        "sector": "Technology",
    }
}
```

**维护策略：**
- 版本控制（Git）
- 定期审查和更新
- 支持通过 PR 提交新映射

## Performance Optimization

### Backend
- **缓存：** LRU cache for search results (1 hour TTL)
- **索引：** 如果使用数据库，在 name/name_cn 字段建立索引
- **限流：** Rate limiting per IP (100 req/min)

### Frontend
- **Debounce：** 300ms 输入防抖
- **虚拟滚动：** 如果结果超过 50 条
- **预加载：** 热门股票数据预加载

## Testing Strategy

### Backend Tests
```python
# tests/test_stock_search.py
def test_exact_ticker_match():
    results = search_stocks("AAPL")
    assert results[0]["ticker"] == "AAPL"

def test_chinese_name_search():
    results = search_stocks("苹果")
    assert results[0]["ticker"] == "AAPL"

def test_fuzzy_match():
    results = search_stocks("appl")  # typo
    assert any(r["ticker"] == "AAPL" for r in results)

def test_empty_query():
    results = search_stocks("")
    assert results == []
```

### Frontend Tests
- Component rendering tests (Jest + React Testing Library)
- Keyboard navigation tests
- API integration tests (MSW for mocking)

## Deployment

### Phase 1 Rollout
1. 部署后端 API（feature flag 控制）
2. 前端灰度发布（10% 用户）
3. 监控性能和错误率
4. 全量发布

### Monitoring
- API 响应时间（P50, P95, P99）
- 搜索成功率（有结果 / 总请求）
- 错误率和类型
- 热门搜索词统计

## Migration Plan

### 代码迁移
1. 提取 `commands.py` 中的映射到独立模块
2. 更新 Lark Bot 引用新模块
3. 添加搜索 API 端点
4. 前端集成新搜索组件

### 数据迁移
- 无需数据迁移（新功能）
- 搜索历史存储在客户端 localStorage

## Future Enhancements

### Phase 3+
- **智能推荐：** 基于用户历史推荐相关股票
- **语义搜索：** 支持"电动车龙头"等自然语言查询
- **多语言：** 繁体中文、日文支持
- **实时补全：** WebSocket 推送实时建议

## Dependencies

### Backend
- 现有：`yfinance`, `fastapi`, `pydantic`
- 新增（可选）：`fuzzywuzzy`, `python-Levenshtein`

### Frontend
- 现有：`react`, `zustand`, `axios`
- 新增：无（使用现有技术栈）

## Risks & Mitigations

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| yfinance API 限流 | 搜索失败 | 本地缓存 + 降级到映射表 |
| 映射数据不全 | 搜索不到股票 | 持续补充 + 用户反馈机制 |
| 前端性能问题 | 输入卡顿 | Debounce + 虚拟滚动 |
| 搜索结果不准确 | 用户体验差 | 调整算法权重 + A/B 测试 |

## Timeline Estimate

- **Phase 1 (MVP):** 3-5 天
  - 后端 API: 1-2 天
  - 前端 UI: 1-2 天
  - 测试和调试: 1 天

- **Phase 2 (增强):** 3-4 天
  - 模糊匹配: 1 天
  - 搜索历史: 1 天
  - 键盘导航: 1 天
  - 测试: 1 天

- **Phase 3 (数据源):** 5-7 天
  - 数据库设计: 1 天
  - 数据采集和清洗: 2-3 天
  - 集成和测试: 2-3 天
