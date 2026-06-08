# AetherCoin (AETH)

**一个完全去中心化、抗ASIC、且具有实际效用的挖矿网络**

## 核心特性

1. **随机工作量证明（Random Proof of Work, RPW）** - 基于RandomX算法，抗ASIC，对CPU/GPU友好
2. **公平启动** - 无预挖，无ICO，所有代币通过挖矿产出
3. **动态难度调整** - 根据网络算力自动调整，确保10分钟出块时间
4. **隐私保护** - 可选的隐私交易功能
5. **智能合约支持** - 兼容EVM，支持DeFi应用

## 经济模型

- **总供应量**: 2100万枚（与比特币相同，确保稀缺性）
- **区块奖励**: 初始50枚，每210,000个区块减半（约4年）
- **减半时间表**:
  - 区块 0-210,000: 50 AETH
  - 区块 210,001-420,000: 25 AETH
  - 区块 420,001-630,000: 12.5 AETH
  - ...以此类推

## 技术架构

```
AetherCoin/
├── src/
│   ├── consensus/          # 共识算法实现
│   │   ├── randomx/        # RandomX算法集成
│   │   ├── pow.rs          # 工作量证明逻辑
│   │   └── difficulty.rs   # 难度调整算法
│   ├── wallet/             # 钱包软件
│   │   ├── desktop/        # 桌面钱包（Electron）
│   │   └── mobile/         # 移动钱包（React Native）
│   ├── contracts/          # 智能合约
│   │   ├── ERC20.sol       # 标准代币合约
│   │   └── Marketplace.sol # 去中心化市场
│   └── node/               # 节点软件
│       ├── p2p.rs          # 点对点网络
│       ├── block.rs        # 区块结构
│       └── mempool.rs      # 交易内存池
├── docs/                   # 文档
│   ├── whitepaper.pdf      # 白皮书
│   ├── technical.md        # 技术文档
│   └── deployment.md       # 部署指南
├── scripts/                # 部署脚本
│   ├── setup.sh            # 一键安装脚本
│   ├── deploy_testnet.sh   # 测试网部署
│   └── deploy_mainnet.sh   # 主网部署
├── tests/                  # 测试套件
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── security/           # 安全测试
├── web/                    # 官网和前端
│   ├── index.html          # 官网首页
│   └── explorer/           # 区块浏览器
└── community/              # 社区资源
    ├── discord/            # Discord机器人
    └── twitter/            # Twitter内容
```

## 快速开始

### 1. 安装节点软件

```bash
# 一键安装（Linux/macOS）
curl -sSL https://raw.githubusercontent.com/aethercoin/aethercoin/main/scripts/setup.sh | bash

# 或手动安装
git clone https://github.com/aethercoin/aethercoin.git
cd aethercoin
cargo build --release
```

### 2. 启动节点

```bash
# 启动全节点
./target/release/aethercoin-node --datadir ~/.aethercoin

# 启动挖矿节点
./target/release/aethercoin-miner --threads=4
```

### 3. 创建钱包

```bash
# 生成新钱包地址
./target/release/aethercoin-wallet generate

# 查看余额
./target/release/aethercoin-wallet balance
```

## 挖矿指南

### CPU挖矿（推荐）

```bash
# 使用CPU挖矿（RandomX算法优化）
./target/release/aethercoin-miner --algorithm=rx/arq --threads=$(nproc)
```

### GPU挖矿

```bash
# 使用GPU挖矿（OpenCL支持）
./target/release/aethercoin-miner --algorithm=rx/arq --gpu --gpu-platform=0
```

### 矿池挖矿

```bash
# 连接矿池挖矿
./target/release/aethercoin-miner --pool=pool.aethercoin.org:3333 --wallet=YOUR_ADDRESS
```

## 智能合约开发

### 部署ERC20代币

```solidity
// contracts/MyToken.sol
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("MyToken", "MTK") {
        _mint(msg.sender, initialSupply);
    }
}
```

### 编译和部署

```bash
# 安装依赖
npm install

# 编译合约
npx hardhat compile

# 部署到测试网
npx hardhat run scripts/deploy.js --network testnet
```

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 安全

如果你发现安全漏洞，请发送邮件至 security@aethercoin.org。请勿在公开Issue中披露安全问题。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系我们

- **网站**: https://aethercoin.org
- **Twitter**: @AetherCoin
- **Discord**: https://discord.gg/aethercoin
- **Telegram**: https://t.me/aethercoin

---

**AetherCoin - 让挖矿回归公平，让价值连接现实**