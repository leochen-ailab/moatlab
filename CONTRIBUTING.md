# Git 分支管理规范

## 策略：GitHub Flow（简化版）

单人开发项目，采用简洁实用的 GitHub Flow。

## 分支结构

```
main (保护分支，始终可用)
 ├── feature/p1-base-agent        # Phase 1 功能
 ├── feature/p1-financial-agent
 ├── fix/dcf-calculation           # 修复
 └── docs/api-reference            # 文档
```

## 工作流

1. 从 `main` 拉功能分支
2. 开发完成后提 PR（附简要说明）
3. Squash Merge 合入 `main`
4. 删除已合入的分支

## 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/<phase>-<模块>` | `feature/p1-financial-agent` |
| 修复 | `fix/<描述>` | `fix/yfinance-timeout` |
| 文档 | `docs/<描述>` | `docs/api-reference` |

## Commit 规范

格式：`<type>: <description>`

| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 |
| `docs` | 文档 |
| `refactor` | 重构 |
| `test` | 测试 |
| `chore` | 构建/配置 |

### 原子性原则

**一个 commit 只做一件事**：
- ✅ 好的示例：
  - `feat: 新增持仓管理工具函数`
  - `feat: 新增 PortfolioAgent`
  - `docs: 更新 API 文档`
- ❌ 不好的示例：
  - `feat: 新增持仓管理功能、修复 bug、更新文档`（混合多个目的）

**为什么要保持原子性**：
- 便于代码审查和理解
- 方便回滚特定变更
- 清晰的项目历史
- 更好的协作体验

**实践建议**：
- 每次 commit 后立即 push 到远端
- 如果一个功能需要多个步骤，拆分成多个 commit
- 使用 `git add -p` 精细控制暂存内容

## 版本标记

每个 Phase 完成后在 `main` 上打 tag：
- `v0.1.0` — Phase 1 完成（MVP 单股分析）
- `v0.2.0` — Phase 2 完成（完整分析链）
- `v0.3.0` — Phase 3 完成（持仓管理 + Web UI）
