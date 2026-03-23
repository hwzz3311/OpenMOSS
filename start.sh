#!/bin/bash
# OpenMOSS 启动脚本
# 功能：创建虚拟环境、安装依赖、构建前端、后台启动服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  OpenMOSS 启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 检测 Python 环境
echo -e "\n${YELLOW}[1/5] 检测 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.11+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "Python 版本: $PYTHON_VERSION"

# 2. 创建虚拟环境
echo -e "\n${YELLOW}[2/5] 创建 Python 虚拟环境...${NC}"
VENV_DIR="$SCRIPT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv "$VENV_DIR"
    echo "虚拟环境创建完成: $VENV_DIR"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 3. 安装 Python 依赖
echo -e "\n${YELLOW}[3/5] 安装 Python 依赖...${NC}"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"
echo -e "${GREEN}Python 依赖安装完成${NC}"

# 4. 构建前端
echo -e "\n${YELLOW}[4/5] 构建前端...${NC}"
if [ -d "$SCRIPT_DIR/webui/node_modules" ]; then
    echo "Node modules 已存在，跳过安装"
else
    echo "安装 Node.js 依赖..."
    cd "$SCRIPT_DIR/webui"
    npm install
    cd "$SCRIPT_DIR"
fi

# 构建前端并部署到 static 目录
cd "$SCRIPT_DIR/webui"
npm run build:deploy
cd "$SCRIPT_DIR"
echo -e "${GREEN}前端构建完成${NC}"

# 5. 启动后端服务
echo -e "\n${YELLOW}[5/5] 启动后端服务...${NC}"

# 检查端口是否已被占用
if lsof -i:6565 &> /dev/null; then
    echo -e "${YELLOW}警告: 端口 6565 已被占用${NC}"
    read -p "是否要杀掉占用端口的进程并继续? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:6565 | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo "启动已取消"
        exit 0
    fi
fi

# 后台启动
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 6565 > "$SCRIPT_DIR/openmoss.log" 2>&1 &
PID=$!

# 等待服务启动
sleep 3

# 检查服务是否成功启动
if ps -p $PID > /dev/null; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  OpenMOSS 启动成功!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "服务地址: ${GREEN}http://localhost:6565${NC}"
    echo -e "API 文档: ${GREEN}http://localhost:6565/api/docs${NC}"
    echo -e "日志文件: $SCRIPT_DIR/openmoss.log"
    echo -e "进程 ID: $PID"
else
    echo -e "${RED}服务启动失败，请检查日志: $SCRIPT_DIR/openmoss.log${NC}"
    exit 1
fi