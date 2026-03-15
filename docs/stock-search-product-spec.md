# Product Spec: 股票分析搜索体验优化

## Context

当前股票分析功能的搜索体验存在以下问题：

**现状：**
- Web UI 只支持精确的 ticker 代码输入（如 AAPL）
- 没有自动补全、模糊匹配或建议功能
- 用户必须知道准确的 ticker 代码才能使用
- 输入错误的 ticker 会导致静默失败（yfinance 返回空数据）
- Lark Bot 有公司名映射功能（80+ 硬编码映射），但 Web UI 没有

**用户痛点：**
1. 不知道公司的 ticker 代码时无法搜索
2. 输入公司名（如"苹果"、"Apple"）无法识别
3. 拼写错误时没有提示或纠正
4. 没有搜索历史或常用股票快捷入口
5. 体验不如主流金融应用（雪球、富途等）

## Product Goals

**核心目标：** 让用户能够快速、准确地找到想要分析的股票，无需记忆 ticker 代码

**成功指标：**
- 用户能通过公司名（中英文）搜索股票
- 搜索响应时间 < 500ms
- 支持模糊匹配和拼写容错
- 减少无效搜索次数

## User Stories

### Story 1: 公司名搜索
**作为** 价值投资者
**我想要** 输入公司名（如"苹果"、"Apple"）就能找到对应股票
**以便** 不需要记忆或查找 ticker 代码

**验收标准：**
- 支持中文公司名：苹果 → AAPL
- 支持英文公司名：Apple → AAPL
- 支持公司全称：Apple Inc. → AAPL
- 支持常见别名：元宇宙 → META

### Story 2: 自动补全
**作为** 用户
**我想要** 输入时看到实时的搜索建议
**以便** 快速选择目标股票，避免输入错误

**验收标准：**
- 输入 2 个字符后显示建议列表
- 建议包含：ticker、公司名、行业
- 支持键盘导航（上下箭头、Enter 选择）
- 支持鼠标点击选择

### Story 3: 模糊匹配
**作为** 用户
**我想要** 输入部分关键词就能找到相关股票
**以便** 在不确定完整名称时也能搜索

**验收标准：**
- "微软" → 显示 MSFT (Microsoft)
- "star" → 显示 SBUX (Starbucks)
- "电动车" → 显示 TSLA (Tesla)
- 按相关度排序结果

### Story 4: 搜索历史
**作为** 频繁用户
**我想要** 看到最近搜索过的股票
**以便** 快速重新分析关注的公司

**验收标准：**
- 显示最近 10 条搜索历史
- 点击历史记录直接触发分析
- 支持清除历史
- 历史存储在 localStorage

### Story 5: 错误提示
**作为** 用户
**我想要** 输入无效 ticker 时得到明确提示
**以便** 知道问题所在并修正

**验收标准：**
- 无匹配结果时显示"未找到相关股票"
- 建议检查拼写或使用公司名搜索
- 提供热门股票快捷入口

## Technical Approach

### Phase 1: 基础搜索 API（MVP）

**后端实现：**
1. 创建 `/api/search/stocks?q={query}` 端点
2. 复用 Lark Bot 的公司名映射逻辑
3. 返回格式：
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "name_cn": "苹果公司",
      "sector": "Technology",
      "exchange": "NASDAQ"
    }
  ]
}
```

**前端实现：**
1. 修改 `AnalysisSearch.tsx` 添加搜索建议下拉
2. 输入时调用搜索 API（debounce 300ms）
3. 显示建议列表，点击填充 ticker

### Phase 2: 增强搜索体验

**功能增强：**
1. 模糊匹配算法（Levenshtein 距离或 fuzzywuzzy）
2. 搜索历史（localStorage）
3. 热门股票快捷入口
4. 键盘导航支持

**数据源扩展：**
1. 考虑使用 yfinance 的 `Ticker.info` 获取公司名
2. 或集成第三方 ticker 搜索 API（如 Alpha Vantage、Polygon.io）
3. 构建本地 ticker 数据库（S&P 500 + 常见中概股）

### Phase 3: 高级功能（未来）

1. 行业/板块筛选
2. 多语言支持（繁体中文）
3. 搜索排序优化（市值、热度）
4. 搜索分析（用户搜索行为统计）

## Design Considerations

### UI/UX
- 搜索框保持简洁，不增加认知负担
- 建议列表最多显示 10 条
- 移动端适配（触摸友好）
- 加载状态明确（loading spinner）

### Performance
- 搜索 API 响应时间 < 500ms
- 前端 debounce 避免频繁请求
- 考虑缓存常见搜索结果

### Data Quality
- 公司名映射需要持续维护
- 优先覆盖 S&P 500 + 热门中概股
- 支持用户反馈错误映射

## Out of Scope (V1)

- 实时股价显示
- 搜索结果分页
- 高级筛选（市值、PE 等）
- 多 ticker 批量分析
- 搜索结果导出

## Success Metrics

**定量指标：**
- 搜索成功率 > 95%（有效 ticker 返回）
- 平均搜索时间 < 3 秒（从输入到选择）
- 搜索历史使用率 > 30%

**定性指标：**
- 用户反馈：搜索体验改善
- 减少"找不到股票"的支持请求

## Implementation Priority

**P0 (Must Have):**
- 公司名搜索 API
- 前端自动补全 UI
- 基础错误处理

**P1 (Should Have):**
- 模糊匹配
- 搜索历史
- 键盘导航

**P2 (Nice to Have):**
- 热门股票快捷入口
- 搜索分析统计
- 多语言支持

## Next Steps

1. Review & approve this spec
2. 技术方案设计（选择搜索算法、数据源）
3. API 设计评审
4. 前端 UI/UX 设计
5. 开发排期规划
