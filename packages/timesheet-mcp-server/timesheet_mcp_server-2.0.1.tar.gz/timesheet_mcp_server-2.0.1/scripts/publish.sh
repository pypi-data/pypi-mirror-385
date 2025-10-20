#!/bin/bash

# 自动化发布脚本 - Timesheet MCP Server V2
# 用法: ./scripts/publish.sh [版本号]

set -e  # 任何错误都停止执行

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="timesheet-mcp-server"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${PROJECT_DIR}/dist"

echo -e "${YELLOW}🚀 开始发布 ${PROJECT_NAME}${NC}"
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

# 第 5 步：上传到 PyPI
echo -e "${YELLOW}⬆️  第 4 步: 上传到 PyPI${NC}"

# 设置 PyPI Token
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmcCJGE0MGUzMzZjLWY0MWQtNGJjOC1hMDEwLTdlNzdmNzNhNmJhZAACKlszLCJjNmMwNDZkNS1hOGU2LTRjYTYtODE4ZS1iYmI3ZWZkMTFlMTAiXQAABiBumk3RMFKS8fDEMgrbEne_PFEVfcLEKA1W-DrVSkzgcQ"

# 上传（使用 --skip-existing 允许覆盖已存在的版本）
twine upload dist/* --skip-existing

echo -e "${GREEN}✓ 上传完成${NC}"
echo ""

# 第 6 步：显示结果
echo -e "${GREEN}✅ 发布成功！${NC}"
echo ""
echo "📦 PyPI 页面: https://pypi.org/project/${PROJECT_NAME}/"
echo ""
echo "用户安装方式:"
echo "  uvx ${PROJECT_NAME}"
echo "  pip install ${PROJECT_NAME}"
echo ""
echo -e "${YELLOW}💡 提示: 重新连接 MCP 服务器以使用最新版本${NC}"
