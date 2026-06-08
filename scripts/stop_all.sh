#!/bin/bash

# AetherCoin 一键停止脚本
# 使用方法: ./scripts/stop_all.sh

set -e

echo "=========================================="
echo "   AetherCoin 一键停止脚本"
echo "=========================================="

# 配置参数
DATA_DIR="$HOME/.aethercoin"
PID_DIR="$DATA_DIR/pids"

# 停止服务
stop_service() {
    local service_name=$1
    local pid_file="$PID_DIR/$service_name.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        
        if kill -0 "$pid" 2>/dev/null; then
            echo "正在停止 $service_name (PID: $pid)..."
            kill "$pid"
            
            # 等待进程停止
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                echo "警告: $service_name 未能在10秒内停止，强制终止"
                kill -9 "$pid"
            else
                echo "✓ $service_name 已停止"
            fi
        else
            echo "警告: $service_name 进程不存在 (PID: $pid)"
        fi
        
        rm -f "$pid_file"
    else
        echo "信息: $service_name 未运行"
    fi
}

# 停止所有服务
stop_all() {
    echo "正在停止所有AetherCoin服务..."
    
    stop_service "web"
    stop_service "miner"
    stop_service "node"
    
    echo ""
    echo "=========================================="
    echo "   所有服务已停止"
    echo "=========================================="
}

# 清理临时文件
cleanup() {
    echo "正在清理临时文件..."
    
    # 清理PID文件
    rm -rf "$PID_DIR"
    
    # 可选: 清理日志文件
    # rm -rf "$DATA_DIR/logs"
    
    echo "✓ 临时文件已清理"
}

# 显示帮助
show_help() {
    echo "AetherCoin 一键停止脚本"
    echo ""
    echo "使用方法:"
    echo "  ./scripts/stop_all.sh          停止所有服务"
    echo "  ./scripts/stop_all.sh --clean  停止服务并清理临时文件"
    echo "  ./scripts/stop_all.sh --help   显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./scripts/stop_all.sh          # 停止所有服务"
    echo "  ./scripts/stop_all.sh --clean  # 停止服务并清理日志和PID文件"
}

# 主函数
main() {
    case "${1:-}" in
        --help|-h)
            show_help
            ;;
        --clean)
            stop_all
            cleanup
            ;;
        "")
            stop_all
            ;;
        *)
            echo "错误: 未知参数 '$1'"
            echo "使用 '--help' 查看帮助信息"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"