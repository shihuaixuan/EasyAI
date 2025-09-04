#!/bin/bash
# 安装模型同步服务脚本

set -e

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo "请不要使用root用户运行此脚本"
   exit 1
fi

# 项目目录
PROJECT_DIR="/Users/twenty/LLM/EasyAI"
SERVICE_FILE="$PROJECT_DIR/scripts/model_sync.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== 安装EasyAI模型同步服务 ==="

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在 $PROJECT_DIR"
    exit 1
fi

# 检查服务文件
if [ ! -f "$SERVICE_FILE" ]; then
    echo "错误: 服务文件不存在 $SERVICE_FILE"
    exit 1
fi

# 创建日志目录
echo "创建日志目录..."
mkdir -p "$PROJECT_DIR/logs"

# 复制服务文件
echo "安装systemd服务文件..."
sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/model-sync.service"

# 重新加载systemd
echo "重新加载systemd..."
sudo systemctl daemon-reload

# 启用服务
echo "启用模型同步服务..."
sudo systemctl enable model-sync.service

echo "=== 安装完成 ==="
echo "使用以下命令管理服务:"
echo "  启动服务: sudo systemctl start model-sync"
echo "  停止服务: sudo systemctl stop model-sync"
echo "  查看状态: sudo systemctl status model-sync"
echo "  查看日志: sudo journalctl -u model-sync -f"
echo ""
echo "服务将在系统启动时自动启动"
