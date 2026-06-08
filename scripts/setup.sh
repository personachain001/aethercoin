#!/bin/bash

# AetherCoin 一键安装脚本
# 使用方法: curl -sSL https://raw.githubusercontent.com/aethercoin/aethercoin/main/scripts/setup.sh | bash

set -e

echo "=========================================="
echo "   AetherCoin 一键安装脚本"
echo "=========================================="

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# 安装依赖
install_dependencies() {
    local os=$(detect_os)
    
    echo "正在安装依赖..."
    
    case $os in
        "debian")
            sudo apt-get update
            sudo apt-get install -y build-essential cmake git curl wget libssl-dev libboost-all-dev
            ;;
        "redhat")
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y cmake git curl wget openssl-devel boost-devel
            ;;
        "macos")
            # 检查是否安装了Homebrew
            if ! command -v brew &> /dev/null; then
                echo "正在安装Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install cmake git curl wget openssl boost
            ;;
        *)
            echo "不支持的操作系统: $os"
            exit 1
            ;;
    esac
}

# 安装Rust
install_rust() {
    if ! command -v rustc &> /dev/null; then
        echo "正在安装Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source $HOME/.cargo/env
    else
        echo "Rust已安装"
    fi
    
    # 更新Rust
    rustup update
}

# 克隆并构建AetherCoin
build_aethercoin() {
    local install_dir="$HOME/.aethercoin"
    
    echo "正在克隆AetherCoin..."
    if [ -d "$install_dir" ]; then
        echo "AetherCoin已存在于 $install_dir，正在更新..."
        cd "$install_dir"
        git pull
    else
        git clone https://github.com/aethercoin/aethercoin.git "$install_dir"
        cd "$install_dir"
    fi
    
    echo "正在构建AetherCoin..."
    cargo build --release
    
    echo "正在安装AetherCoin..."
    sudo cp target/release/aethercoin-node /usr/local/bin/
    sudo cp target/release/aethercoin-miner /usr/local/bin/
    sudo cp target/release/aethercoin-wallet /usr/local/bin/
    
    echo "✓ AetherCoin安装完成！"
}

# 配置节点
configure_node() {
    local data_dir="$HOME/.aethercoin/data"
    
    echo "正在配置节点..."
    mkdir -p "$data_dir"
    
    # 创建默认配置文件
    cat > "$data_dir/config.toml" << EOF
# AetherCoin节点配置

[network]
port = 8333
max_peers = 50

[storage]
data_dir = "$data_dir"

[mining]
threads = 4
algorithm = "rx/arq"

[logging]
level = "info"
EOF

    echo "✓ 节点配置完成！"
}

# 创建启动脚本
create_start_scripts() {
    local bin_dir="/usr/local/bin"
    
    echo "正在创建启动脚本..."
    
    # 启动节点脚本
    cat > "$bin_dir/aethercoin-start" << 'EOF'
#!/bin/bash
echo "正在启动AetherCoin节点..."
aethercoin-node --datadir ~/.aethercoin/data "$@"
EOF
    chmod +x "$bin_dir/aethercoin-start"
    
    # 启动挖矿脚本
    cat > "$bin_dir/aethercoin-mine" << 'EOF'
#!/bin/bash
echo "正在启动AetherCoin挖矿..."
aethercoin-miner --datadir ~/.aethercoin/data --threads=$(nproc) "$@"
EOF
    chmod +x "$bin_dir/aethercoin-mine"
    
    # 创建钱包脚本
    cat > "$bin_dir/aethercoin-wallet-create" << 'EOF'
#!/bin/bash
echo "正在创建AetherCoin钱包..."
aethercoin-wallet generate --datadir ~/.aethercoin/data "$@"
EOF
    chmod +x "$bin_dir/aethercoin-wallet-create"
    
    echo "✓ 启动脚本创建完成！"
}

# 打印使用说明
print_usage() {
    echo ""
    echo "=========================================="
    echo "   安装完成！"
    echo "=========================================="
    echo ""
    echo "使用方法："
    echo ""
    echo "1. 启动节点："
    echo "   aethercoin-start"
    echo ""
    echo "2. 开始挖矿："
    echo "   aethercoin-mine"
    echo ""
    echo "3. 创建钱包："
    echo "   aethercoin-wallet-create"
    echo ""
    echo "4. 查看帮助："
    echo "   aethercoin-node --help"
    echo "   aethercoin-miner --help"
    echo "   aethercoin-wallet --help"
    echo ""
    echo "5. 查看状态："
    echo "   aethercoin-node status"
    echo ""
    echo "文档: https://docs.aethercoin.org"
    echo "社区: https://discord.gg/aethercoin"
    echo ""
    echo "祝您挖矿愉快！"
    echo "=========================================="
}

# 主函数
main() {
    echo "开始安装AetherCoin..."
    
    install_dependencies
    install_rust
    build_aethercoin
    configure_node
    create_start_scripts
    print_usage
}

# 运行主函数
main "$@"