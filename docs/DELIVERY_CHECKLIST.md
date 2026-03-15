# MoatLab 交付检查清单

> 所有代码交付前必须完成自测，确保质量准出

---

## 1. 编译检查

### 前端
```bash
cd frontend
npm run build
```

**通过标准**：
- ✅ 无 TypeScript 编译错误
- ✅ 无 ESLint 错误
- ✅ 构建成功生成 dist 目录

### 后端
```bash
uv run python -m py_compile src/moatlab/**/*.py
```

**通过标准**：
- ✅ 无 Python 语法错误
- ✅ 所有模块可正常导入

---

## 2. 单元测试

### 后端测试
```bash
uv run pytest tests/ -v
```

**通过标准**：
- ✅ 所有测试用例通过
- ✅ 覆盖率 > 80%（核心业务逻辑）

### 前端测试（可选）
```bash
cd frontend
npm run test
```

---

## 3. 功能自测

### 3.1 后端 API 自测

#### 健康检查
```bash
curl http://localhost:8000/health
# 预期: {"status":"ok","service":"moatlab"}
```

#### 持仓管理
```bash
# 获取持仓
curl http://localhost:8000/api/portfolio

# 买入
curl -X POST http://localhost:8000/api/portfolio/buy \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","shares":10,"price":150.0}'

# 卖出
curl -X POST http://localhost:8000/api/portfolio/sell \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","shares":5,"price":160.0}'

# 业绩汇总
curl http://localhost:8000/api/portfolio/performance

# 交易历史
curl http://localhost:8000/api/portfolio/history
```

#### 股票分析
```bash
curl -X POST http://localhost:8000/api/analyze/AAPL \
  -H "Content-Type: application/json" \
  -d '{"mode":"financial"}'
```

#### 股票筛选
```bash
curl -X POST http://localhost:8000/api/screen \
  -H "Content-Type: application/json" \
  -d '{"roe_min":0.15,"debt_to_equity_max":0.5}'
```

**通过标准**：
- ✅ 所有 API 返回正确的 HTTP 状态码
- ✅ 响应数据格式符合预期
- ✅ 错误处理正确（400/404/500）

### 3.2 前端 UI 自测

访问 http://localhost:5175（或实际端口）

#### 页面加载
- ✅ 首页正常显示
- ✅ 左侧导航栏显示所有菜单项
- ✅ 顶部 Header 显示 Logo 和导航

#### 持仓管理页面 (`/portfolio`)
- ✅ 概览卡片显示总成本、总市值、总收益、收益率
- ✅ 持仓列表表格正常显示
- ✅ 点击"买入"按钮弹出表单
- ✅ 填写表单并提交成功
- ✅ 持仓列表实时更新
- ✅ 点击"卖出"按钮弹出表单
- ✅ 卖出操作成功并更新数据
- ✅ 交易历史表格显示所有记录
- ✅ 持仓分布饼图正常渲染
- ✅ 点击"刷新"按钮重新加载数据

#### 股票分析页面 (`/analyze`)
- ✅ 搜索框和模式选择正常显示
- ✅ 输入股票代码并选择分析模式
- ✅ 点击"开始分析"显示进度条
- ✅ 分析完成后显示结果卡片
- ✅ 投资建议标签正确显示（BUY/HOLD/SELL/PASS）
- ✅ 分析报告内容正常渲染
- ✅ 右侧历史列表显示最近分析记录
- ✅ 点击历史记录重新分析
- ✅ 清空历史功能正常

#### 股票筛选页面 (`/screen`)
- ✅ 筛选条件表单正常显示
- ✅ 填写筛选条件并提交
- ✅ 筛选结果正常显示
- ✅ 点击"重置"清空条件
- ✅ 点击"刷新"重新筛选

#### 导航功能
- ✅ 点击左侧导航栏切换页面
- ✅ 点击顶部导航栏切换页面
- ✅ 当前页面高亮显示
- ✅ 浏览器前进/后退按钮正常工作

#### 错误处理
- ✅ 后端服务停止时显示错误提示
- ✅ 无效股票代码显示错误提示
- ✅ 表单验证错误正确显示
- ✅ 网络错误不导致页面崩溃

---

## 4. 代码质量检查

### 代码风格
- ✅ Python 代码符合 PEP 8 规范
- ✅ TypeScript 代码符合 ESLint 规则
- ✅ 无未使用的导入和变量
- ✅ 无 console.log 调试代码

### 代码审查
- ✅ 函数命名清晰，职责单一
- ✅ 无重复代码（DRY 原则）
- ✅ 错误处理完善
- ✅ 类型注解完整（TypeScript/Python）

### 安全检查
- ✅ 无硬编码的敏感信息（API Key、密码）
- ✅ 输入验证完善
- ✅ SQL 注入防护（使用参数化查询）
- ✅ XSS 防护（前端输入转义）

---

## 5. 文档更新

- ✅ README.md 更新（如有新功能）
- ✅ PROGRESS.md 更新进度
- ✅ API 文档更新（如有新接口）
- ✅ 代码注释完善（复杂逻辑）

---

## 6. Git 提交规范

### Commit Message 格式
```
<type>: <中文描述>

[可选的详细说明]
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

### 提交前检查
- ✅ 一个 commit 只表达一个目的（原子性）
- ✅ Commit message 清晰描述改动
- ✅ 无调试代码和临时文件
- ✅ 代码已格式化

### 推送前检查
```bash
# 确保本地测试通过
uv run pytest tests/ -v

# 确保前端构建成功
cd frontend && npm run build

# 推送到远端
git push origin <branch-name>
```

---

## 7. PR 创建规范

### PR 标题
```
<type>: <中文描述>
```

### PR 描述模板
```markdown
## 改动内容
- 新增/修复/优化了什么功能

## 测试情况
- [ ] 单元测试通过
- [ ] 功能自测通过
- [ ] 代码审查完成

## 相关 Issue
Closes #<issue-number>

## 截图（如有 UI 改动）
[粘贴截图]
```

---

## 8. 快速自测脚本

创建 `scripts/self-test.sh`：

```bash
#!/bin/bash
set -e

echo "=== MoatLab 自测脚本 ==="

# 1. 后端测试
echo "1. 运行后端测试..."
uv run pytest tests/ -v

# 2. 前端构建
echo "2. 前端构建检查..."
cd frontend
npm run build
cd ..

# 3. API 健康检查
echo "3. API 健康检查..."
curl -f http://localhost:8000/health || echo "⚠️  后端服务未启动"

echo "✅ 自测完成！"
```

使用方法：
```bash
chmod +x scripts/self-test.sh
./scripts/self-test.sh
```

---

## 9. 交付清单总结

**每次交付前必须确认**：

- [ ] 编译无错误
- [ ] 测试全部通过
- [ ] 功能自测完成
- [ ] 代码质量检查通过
- [ ] 文档已更新
- [ ] Git 提交规范
- [ ] PR 描述完整

**只有所有项目都打勾，才能合并到 main 分支！**

---

## 10. 常见问题排查

### 前端无法连接后端
```bash
# 检查后端是否启动
curl http://localhost:8000/health

# 检查 CORS 配置
# 确保 server.py 中有 CORS 中间件
```

### 前端构建失败
```bash
# 清理缓存重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 后端测试失败
```bash
# 检查数据库状态
ls -la ~/.moatlab/portfolio.db

# 重置测试数据库
rm -f ~/.moatlab/test_portfolio.db
uv run pytest tests/ -v
```

---

**记住：质量是交付的第一要务，宁可慢一点，也要确保每次交付都是高质量的！**
