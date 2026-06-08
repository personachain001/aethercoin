#!/bin/bash

# AetherCoin 一键启动脚本
# 使用方法: ./scripts/start_all.sh

set -e

echo "=========================================="
echo "   AetherCoin 一键启动脚本"
echo "=========================================="

# 配置参数
WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$HOME/.aethercoin"
LOG_DIR="$DATA_DIR/logs"
PID_DIR="$DATA_DIR/pids"

# 创建必要目录
mkdir -p "$DATA_DIR" "$LOG_DIR" "$PID_DIR"

# 检查依赖
check_dependencies() {
    echo "正在检查依赖..."
    
    if ! command -v cargo &> /dev/null; then
        echo "错误: 未找到Cargo"
        echo "请安装Rust: https://rustup.rs/"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "错误: 未找到Node.js"
        echo "请安装Node.js: https://nodejs.org/"
        exit 1
    fi
    
    echo "✓ 依赖检查通过"
}

# 构建项目
build_project() {
    echo "正在构建AetherCoin..."
    
    cd "$WORK_DIR"
    cargo build --release
    
    echo "✓ 构建完成"
}

# 启动节点
start_node() {
    echo "正在启动AetherCoin节点..."
    
    NODE_BIN="$WORK_DIR/target/release/aethercoin-node"
    NODE_LOG="$LOG_DIR/node.log"
    NODE_PID="$PID_DIR/node.pid"
    
    if [ -f "$NODE_PID" ] && kill -0 $(cat "$NODE_PID") 2>/dev/null; then
        echo "节点已在运行中 (PID: $(cat $NODE_PID))"
        return
    fi
    
    # 启动节点
    nohup "$NODE_BIN" --datadir "$DATA_DIR" > "$NODE_LOG" 2>&1 &
    echo $! > "$NODE_PID"
    
    echo "✓ 节点已启动 (PID: $(cat $NODE_PID))"
    echo "  日志文件: $NODE_LOG"
}

# 启动挖矿
start_mining() {
    echo "正在启动挖矿..."
    
    MINER_BIN="$WORK_DIR/target/release/aethercoin-miner"
    MINER_LOG="$LOG_DIR/miner.log"
    MINER_PID="$PID_DIR/miner.pid"
    
    if [ -f "$MINER_PID" ] && kill -0 $(cat "$MINER_PID") 2>/dev/null; then
        echo "挖矿已在运行中 (PID: $(cat $MINER_PID))"
        return
    fi
    
    # 获取CPU核心数
    CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    
    # 启动挖矿
    nohup "$MINER_BIN" --datadir "$DATA_DIR" --threads=$CORES --algorithm=rx/arq > "$MINER_LOG" 2>&1 &
    echo $! > "$MINER_PID"
    
    echo "✓ 挖矿已启动 (PID: $(cat $MINER_PID))"
    echo "  使用核心数: $CORES"
    echo "  日志文件: $MINER_LOG"
}

# 启动Web服务器
start_web() {
    echo "正在启动Web服务器..."
    
    WEB_DIR="$WORK_DIR/web"
    WEB_LOG="$LOG_DIR/web.log"
    WEB_PID="$PID_DIR/web.pid"
    
    if [ -f "$WEB_PID" ] && kill -0 $(cat "$WEB_PID") 2>/dev/null; then
        echo "Web服务器已在运行中 (PID: $(cat $WEB_PID))"
        return
    fi
    
    # 检查Python是否可用
    if command -v python3 &> /dev/null; then
        cd "$WEB_DIR"
        nohup python3 -m http.server 8080 > "$WEB_LOG" 2>&1 &
        echo $! > "$WEB_PID"
        
        echo "✓ Web服务器已启动 (PID: $(cat $WEB_PID))"
        echo "  访问地址: http://localhost:8080"
        echo "  日志文件: $WEB_LOG"
    else
        echo "警告: 未找到Python3，无法启动Web服务器"
        echo "请安装Python3或手动启动Web服务器"
    fi
}

# 显示状态
show_status() {
    echo ""
    echo "=========================================="
    echo "   AetherCoin 服务状态"
    echo "=========================================="
    
    # 检查节点状态
    if [ -f "$PID_DIR/node.pid" ] && kill -0 $(cat "$PID_DIR/node.pid") 2>/dev/null; then
        echo "✓ 节点: 运行中 (PID: $(cat $PID_DIR/node.pid))"
    else
        echo "✗ 节点: 未运行"
    fi
    
    # 检查挖矿状态
    if [ -f "$PID_DIR/miner.pid" ] && kill -0 $(cat "$PID_DIR/miner.pid") 2>/dev/null; then
        echo "✓ 挖矿: 运行中 (PID: $(cat $PID_DIR/miner.pid))"
    else
        echo "✗ 挖矿: 未运行"
    fi
    
    # 检查Web服务器状态
    if [ -f "$PID_DIR/web.pid" ] && kill -0 $(cat "$PID_DIR/web.pid") 2>/dev/null; then
        echo "✓ Web服务器: 运行中 (PID: $(cat $PID_DIR/web.pid))"
    else
        echo "✗ Web服务器: 未运行"
    fi
    
    echo ""
    echo "访问以下地址："
    echo "  官网: http://localhost:8080"
    echo "  区块浏览器: http://localhost:8080/explorer/"
    echo "  钱包: http://localhost:8080/wallet/"
    echo ""
    echo "日志文件："
    echo "  节点日志: $LOG_DIR/node.log"
    echo "  挖矿日志: $LOG_DIR/miner.log"
    echo "  Web日志: $LOG_DIR/web.log"
    echo ""
    echo "停止所有服务: ./scripts/stop_all.sh"
    echo "=========================================="
}

# 主函数
main() {
    echo "开始启动AetherCoin服务..."
    
    check_dependencies
    build_project
    start_node
    start_mining
    start_web
    show_status
}

# 运行主函数
main "$@"