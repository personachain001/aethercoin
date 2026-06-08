#!/bin/bash

# AetherCoin 测试网部署脚本
# 使用方法: ./deploy_testnet.sh

set -e

echo "=========================================="
echo "   AetherCoin 测试网部署脚本"
echo "=========================================="

# 配置参数
NETWORK="testnet"
RPC_URL="https://rpc.testnet.aethercoin.org"
CHAIN_ID=31337
INITIAL_SUPPLY=10000000000000000000000000000  # 10亿 AETH (18位小数)

# 检查依赖
check_dependencies() {
    echo "正在检查依赖..."
    
    if ! command -v node &> /dev/null; then
        echo "错误: 未找到Node.js"
        echo "请安装Node.js: https://nodejs.org/"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "错误: 未找到npm"
        echo "请安装npm: https://www.npmjs.com/"
        exit 1
    fi
    
    echo "✓ 依赖检查通过"
}

# 安装依赖
install_dependencies() {
    echo "正在安装依赖..."
    
    cd src/contracts
    
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    echo "✓ 依赖安装完成"
}

# 编译合约
compile_contracts() {
    echo "正在编译智能合约..."
    
    cd src/contracts
    npx hardhat compile
    
    echo "✓ 合约编译完成"
}

# 部署合约
deploy_contracts() {
    echo "正在部署智能合约到测试网..."
    
    cd src/contracts
    
    # 创建部署脚本
    cat > scripts/deploy.js << EOF
const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("部署账户:", deployer.address);
    console.log("账户余额:", (await deployer.getBalance()).toString());

    // 部署AetherCoin合约
    const AetherCoin = await ethers.getContractFactory("AetherCoin");
    const aethercoin = await AetherCoin.deploy(
        "AetherCoin",
        "AETH",
        18,
        ${INITIAL_SUPPLY}
    );
    await aethercoin.deployed();
    
    console.log("AetherCoin合约地址:", aethercoin.address);
    
    // 部署市场合约
    const Marketplace = await ethers.getContractFactory("Marketplace");
    const marketplace = await Marketplace.deploy(aethercoin.address);
    await marketplace.deployed();
    
    console.log("Marketplace合约地址:", marketplace.address);
    
    // 保存合约地址
    const fs = require('fs');
    const contractAddresses = {
        AetherCoin: aethercoin.address,
        Marketplace: marketplace.address
    };
    
    fs.writeFileSync(
        '../docs/contract_addresses.json',
        JSON.stringify(contractAddresses, null, 2)
    );
    
    console.log("合约地址已保存到 docs/contract_addresses.json");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
EOF

    # 运行部署脚本
    npx hardhat run scripts/deploy.js --network testnet
    
    echo "✓ 合约部署完成"
}

# 验证合约
verify_contracts() {
    echo "正在验证智能合约..."
    
    cd src/contracts
    
    # 读取合约地址
    if [ -f "../docs/contract_addresses.json" ]; then
        AETHERCOIN_ADDRESS=$(jq -r '.AetherCoin' ../docs/contract_addresses.json)
        MARKETPLACE_ADDRESS=$(jq -r '.Marketplace' ../docs/contract_addresses.json)
        
        echo "验证AetherCoin合约..."
        npx hardhat verify --network testnet $AETHERCOIN_ADDRESS "AetherCoin" "AETH" 18 ${INITIAL_SUPPLY}
        
        echo "验证Marketplace合约..."
        npx hardhat verify --network testnet $MARKETPLACE_ADDRESS $AETHERCOIN_ADDRESS
        
        echo "✓ 合约验证完成"
    else
        echo "警告: 未找到合约地址文件，跳过验证"
    fi
}

# 启动测试节点
start_test_node() {
    echo "正在启动测试节点..."
    
    cd src/contracts
    
    # 启动Hardhat本地节点
    npx hardhat node &
    
    # 等待节点启动
    sleep 5
    
    echo "✓ 测试节点已启动"
    echo "RPC地址: http://127.0.0.1:8545"
    echo "链ID: ${CHAIN_ID}"
}

# 创建示例账户
create_sample_accounts() {
    echo "正在创建示例账户..."
    
    cd src/contracts
    
    # 创建示例账户
    cat > scripts/create_accounts.js << EOF
const { ethers } = require("hardhat");

async function main() {
    const signers = await ethers.getSigners();
    
    console.log("示例账户:");
    for (let i = 0; i < 5; i++) {
        console.log(\`账户 \${i+1}: \${signers[i].address}\`);
        console.log(\`  私钥: \${signers[i].privateKey}\`);
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
EOF

    npx hardhat run scripts/create_accounts.js --network localhost
    
    echo "✓ 示例账户创建完成"
}

# 打印部署信息
print_deployment_info() {
    echo ""
    echo "=========================================="
    echo "   测试网部署完成！"
    echo "=========================================="
    echo ""
    echo "网络信息:"
    echo "  网络名称: AetherCoin Testnet"
    echo "  RPC URL: ${RPC_URL}"
    echo "  链ID: ${CHAIN_ID}"
    echo ""
    echo "合约地址:"
    if [ -f "docs/contract_addresses.json" ]; then
        cat docs/contract_addresses.json
    else
        echo "  未找到合约地址文件"
    fi
    echo ""
    echo "下一步:"
    echo "1. 导入私钥到MetaMask"
    echo "2. 添加自定义网络"
    echo "3. 开始测试DApp"
    echo ""
    echo "文档: https://docs.aethercoin.org/testnet"
    echo "=========================================="
}

# 主函数
main() {
    echo "开始部署AetherCoin测试网..."
    
    check_dependencies
    install_dependencies
    compile_contracts
    deploy_contracts
    verify_contracts
    start_test_node
    create_sample_accounts
    print_deployment_info
}

# 运行主函数
main "$@"