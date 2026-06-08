# AetherCoin 部署指南

本指南将带你从零开始部署AetherCoin网络，包括测试网和主网。

## 前置要求

### 系统要求
- **操作系统**: Linux (Ubuntu 20.04+), macOS (10.15+), 或 Windows 10+
- **内存**: 最少4GB RAM
- **存储**: 最少20GB可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- **Node.js**: v16.0.0 或更高版本
- **npm**: v8.0.0 或更高版本
- **Rust**: 最新稳定版本
- **Git**: 最新版本

## 第一步：环境准备

### 1.1 安装依赖

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y build-essential cmake git curl wget libssl-dev libboost-all-dev
```

#### macOS
```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install cmake git curl wget openssl boost
```

#### Windows
1. 安装 [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install)
2. 在WSL中运行Ubuntu命令

### 1.2 安装Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
```

### 1.3 安装Node.js
```bash
# 使用nvm安装Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

## 第二步：获取代码

### 2.1 克隆仓库
```bash
git clone https://github.com/aethercoin/aethercoin.git
cd aethercoin
```

### 2.2 构建项目
```bash
# 构建核心组件
cargo build --release

# 安装依赖
cd src/contracts
npm install
cd ../..
```

## 第三步：部署测试网

### 3.1 启动本地测试网
```bash
# 启动Hardhat本地节点
cd src/contracts
npx hardhat node
```

### 3.2 部署智能合约
```bash
# 在新的终端窗口中
cd src/contracts
npx hardhat run scripts/deploy.js --network localhost
```

### 3.3 验证部署
```bash
# 检查合约地址
cat ../docs/contract_addresses.json
```

### 3.4 启动节点软件
```bash
# 在新的终端窗口中
./target/release/aethercoin-node --datadir ~/.aethercoin/testnet
```

## 第四步：部署主网

### 4.1 准备主网配置

创建主网配置文件 `config/mainnet.toml`:
```toml
[network]
port = 8333
max_peers = 100
bootstrap_nodes = [
    "node1.aethercoin.org:8333",
    "node2.aethercoin.org:8333"
]

[storage]
data_dir = "~/.aethercoin/mainnet"

[mining]
threads = 8
algorithm = "rx/arq"

[logging]
level = "info"
```

### 4.2 生成创世区块
```bash
# 生成创世区块
./target/release/aethercoin-node generate-genesis --config config/mainnet.toml
```

### 4.3 启动主网节点
```bash
# 启动第一个节点
./target/release/aethercoin-node --datadir ~/.aethercoin/mainnet --config config/mainnet.toml
```

### 4.4 部署主网智能合约
```bash
# 部署到以太坊主网 (需要ETH支付Gas费)
cd src/contracts
npx hardhat run scripts/deploy.js --network mainnet
```

## 第五步：配置钱包

### 5.1 创建钱包
```bash
# 生成新钱包地址
./target/release/aethercoin-wallet generate --datadir ~/.aethercoin/wallet
```

### 5.2 备份钱包
```bash
# 备份钱包文件
cp ~/.aethercoin/wallet/wallet.dat ~/backup/wallet_$(date +%Y%m%d).dat
```

### 5.3 导入到MetaMask
1. 打开MetaMask浏览器插件
2. 点击"导入账户"
3. 选择"私钥"导入方式
4. 粘贴你的私钥

## 第六步：开始挖矿

### 6.1 CPU挖矿
```bash
# 使用所有CPU核心挖矿
./target/release/aethercoin-miner \
    --datadir ~/.aethercoin/mainnet \
    --threads=$(nproc) \
    --algorithm=rx/arq
```

### 6.2 GPU挖矿
```bash
# 使用GPU挖矿
./target/release/aethercoin-miner \
    --datadir ~/.aethercoin/mainnet \
    --gpu \
    --gpu-platform=0 \
    --algorithm=rx/arq
```

### 6.3 矿池挖矿
```bash
# 连接矿池
./target/release/aethercoin-miner \
    --pool=pool.aethercoin.org:3333 \
    --wallet=YOUR_WALLET_ADDRESS \
    --algorithm=rx/arq
```

## 第七步：社区启动

### 7.1 创建社交媒体账号
1. **Twitter**: @AetherCoin
2. **Discord**: 创建AetherCoin服务器
3. **Reddit**: r/AetherCoin
4. **Telegram**: @AetherCoinOfficial

### 7.2 发布公告
使用提供的社区内容模板发布项目介绍。

### 7.3 吸引早期用户
1. 在加密货币论坛发布项目介绍
2. 联系加密货币媒体
3. 举办AMA活动

## 第八步：监控和维护

### 8.1 监控节点状态
```bash
# 查看节点状态
./target/release/aethercoin-node status

# 查看网络信息
./target/release/aethercoin-node network-info
```

### 8.2 日志管理
```bash
# 查看日志
tail -f ~/.aethercoin/mainnet/logs/node.log
```

### 8.3 备份策略
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz ~/.aethercoin/mainnet
EOF

chmod +x backup.sh
```

## 故障排除

### 常见问题

#### 1. 编译错误
```bash
# 清理并重新编译
cargo clean
cargo build --release
```

#### 2. 网络连接问题
```bash
# 检查防火墙设置
sudo ufw allow 8333/tcp

# 检查端口占用
netstat -tulpn | grep 8333
```

#### 3. 钱包同步问题
```bash
# 重新同步钱包
./target/release/aethercoin-wallet resync --datadir ~/.aethercoin/wallet
```

### 获取帮助
- **GitHub Issues**: https://github.com/aethercoin/aethercoin/issues
- **Discord社区**: https://discord.gg/aethercoin
- **文档**: https://docs.aethercoin.org

## 下一步

1. **开发DApp**: 基于AetherCoin智能合约开发去中心化应用
2. **加入治理**: 参与社区投票，共同决定项目发展方向
3. **生态建设**: 为AetherCoin生态系统做出贡献

---

**恭喜！你已经成功部署了AetherCoin网络！**

如有任何问题，请随时在社区中提问。