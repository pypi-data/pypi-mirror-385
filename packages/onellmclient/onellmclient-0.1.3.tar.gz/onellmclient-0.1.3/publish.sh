#!/bin/bash
# 发布脚本 - 构建并上传包到 PyPI
# 用法:
#   ./publish.sh              # 上传到正式 PyPI
#   ./publish.sh --dry-run    # 只构建不上传

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== 开始发布流程 ===${NC}"

# 1. 清理旧的构建文件
echo -e "\n${GREEN}[1/4] 清理旧的构建文件...${NC}"
rm -rf dist/
rm -rf build/
rm -rf *.egg-info

# 2. 构建包
echo -e "\n${GREEN}[2/4] 构建包...${NC}"
uv build

# 3. 检查包内容
echo -e "\n${GREEN}[3/4] 检查包内容...${NC}"
uv run twine check dist/*

# 4. 上传到 PyPI
if [ "$1" = "--dry-run" ]; then
    echo -e "\n${YELLOW}[4/4] 干运行模式，跳过上传${NC}"
    echo -e "\n${GREEN}构建成功！文件位于 dist/ 目录:${NC}"
    ls -lh dist/
    echo -e "\n${GREEN}=== 发布流程完成 ===${NC}"
    exit 0
fi

echo -e "\n${YELLOW}[4/4] 准备上传到正式 PyPI...${NC}"
read -p "确认上传? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}开始上传到正式 PyPI...${NC}"
    uv run twine upload dist/*
    echo -e "\n${GREEN}✓ 成功发布到 PyPI!${NC}"
    echo -e "${BLUE}查看: https://pypi.org/project/onellmclient/${NC}"
    echo -e "\n${GREEN}=== 发布流程完成 ===${NC}"
else
    echo -e "\n${RED}已取消上传${NC}"
    exit 1
fi

