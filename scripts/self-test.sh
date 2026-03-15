#!/bin/bash
set -e

echo "=== MoatLab 自测脚本 ==="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 后端测试
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  运行后端测试..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if uv run pytest tests/ -v --tb=short; then
    echo -e "${GREEN}✅ 后端测试通过${NC}"
else
    echo -e "${RED}❌ 后端测试失败${NC}"
    exit 1
fi
echo ""

# 2. 前端构建
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  前端构建检查..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd frontend
if npm run build; then
    echo -e "${GREEN}✅ 前端构建成功${NC}"
else
    echo -e "${RED}❌ 前端构建失败${NC}"
    exit 1
fi
cd ..
echo ""

# 3. API 健康检查
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  API 健康检查..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务正常运行${NC}"
    curl -s http://localhost:8000/health | jq .
else
    echo -e "${YELLOW}⚠️  后端服务未启动（跳过 API 测试）${NC}"
    echo "   提示: 运行 'uv run moatlab serve' 启动后端服务"
fi
echo ""

# 4. 代码质量检查
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  代码质量检查..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查是否有未提交的调试代码
if git grep -n "console.log" frontend/src/ 2>/dev/null | grep -v "node_modules"; then
    echo -e "${YELLOW}⚠️  发现 console.log 调试代码${NC}"
else
    echo -e "${GREEN}✅ 无调试代码${NC}"
fi

# 检查是否有 TODO 注释
TODO_COUNT=$(git grep -n "TODO\|FIXME" src/ frontend/src/ 2>/dev/null | wc -l || echo 0)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $TODO_COUNT 个 TODO/FIXME 注释${NC}"
else
    echo -e "${GREEN}✅ 无待办事项${NC}"
fi
echo ""

# 5. Git 状态检查
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Git 状态检查..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  有未提交的改动${NC}"
    git status --short
else
    echo -e "${GREEN}✅ 工作区干净${NC}"
fi
echo ""

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ 自测完成！${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 交付前检查清单："
echo "  [ ] 所有测试通过"
echo "  [ ] 前端构建成功"
echo "  [ ] 功能自测完成"
echo "  [ ] 代码已审查"
echo "  [ ] 文档已更新"
echo "  [ ] Commit message 规范"
echo ""
echo "准备好交付了吗？ 🚀"
