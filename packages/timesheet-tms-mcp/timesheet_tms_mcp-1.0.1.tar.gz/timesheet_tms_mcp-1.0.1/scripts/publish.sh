#!/bin/bash

# 发布脚本 - Timesheet MCP Server V2
# 使用 GitHub Releases 方式分发
# 用法: ./scripts/publish.sh [版本号]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="timesheet-tms-mcp"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${PROJECT_DIR}/dist"
VERSION=$(grep 'version = ' "${PROJECT_DIR}/pyproject.toml" | head -1 | sed 's/.*version = "\([^"]*\)".*/\1/')

echo -e "${YELLOW}🚀 开始发布 ${PROJECT_NAME}${NC}"
echo "版本: ${VERSION}"
echo "项目目录: ${PROJECT_DIR}"
echo ""

# 第 1 步：进入项目目录
cd "${PROJECT_DIR}"

# 第 2 步：清理旧的构建文件
echo -e "${YELLOW}📦 第 1 步: 清理旧的构建文件${NC}"
rm -rf build/ dist/ *.egg-info
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 第 3 步：构建包
echo -e "${YELLOW}🔨 第 2 步: 构建包${NC}"
if command -v python3 &> /dev/null; then
    python3 -m build
elif command -v python &> /dev/null; then
    python -m build
else
    echo -e "${RED}✗ 找不到 Python${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 构建完成${NC}"
echo ""

# 第 4 步：检查包
echo -e "${YELLOW}🔍 第 3 步: 检查包${NC}"
if command -v twine &> /dev/null; then
    twine check dist/*
else
    echo -e "${YELLOW}⚠ 警告: twine 未安装，跳过检查${NC}"
fi
echo -e "${GREEN}✓ 检查完成${NC}"
echo ""

# 第 5 步：发布说明
echo -e "${YELLOW}📝 第 4 步: 发布说明${NC}"
echo ""
echo -e "${GREEN}✅ 包已构建完成！${NC}"
echo ""
echo "📦 生成的文件:"
ls -lh dist/
echo ""
echo "🚀 发布方式:"
echo ""
echo "方式 1: 上传到 PyPI (需要凭证)"
echo "  twine upload dist/*"
echo ""
echo "方式 2: 上传到 GitHub Releases"
echo "  gh release create v${VERSION} dist/* --title \"Release ${VERSION}\""
echo ""
echo "方式 3: 用户从 GitHub 直接安装"
echo "  pip install git+https://github.com/yangyuezheng/ai-emp@main#subdirectory=timesheet-mcp-server-v2"
echo ""
echo "方式 4: 用户从 GitHub Releases 直接安装轮子文件"
echo "  pip install https://github.com/yangyuezheng/ai-emp/releases/download/v${VERSION}/timesheet_tms_mcp-${VERSION}-py3-none-any.whl"
echo ""
