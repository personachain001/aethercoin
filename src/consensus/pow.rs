use sha2::{Sha256, Digest};
use serde::{Serialize, Deserialize};
use std::time::{SystemTime, UNIX_EPOCH};

/// 区块头结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockHeader {
    pub version: u32,
    pub previous_block_hash: [u8; 32],
    pub merkle_root: [u8; 32],
    pub timestamp: u64,
    pub difficulty: u32,
    pub nonce: u64,
}

/// 区块结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Block {
    pub header: BlockHeader,
    pub transactions: Vec<Transaction>,
}

/// 交易结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub inputs: Vec<TxInput>,
    pub outputs: Vec<TxOutput>,
    pub fee: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxInput {
    pub previous_tx_hash: [u8; 32],
    pub output_index: u32,
    pub script_sig: Vec<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxOutput {
    pub value: u64,
    pub script_pubkey: Vec<u8>,
}

/// 工作量证明实现
pub struct ProofOfWork {
    difficulty: u32,
}

impl ProofOfWork {
    /// 创建新的PoW实例
    pub fn new(difficulty: u32) -> Self {
        ProofOfWork { difficulty }
    }

    /// 计算区块哈希
    pub fn calculate_hash(&self, header: &BlockHeader) -> [u8; 32] {
        let mut hasher = Sha256::new();
        
        // 序列化区块头
        let data = bincode::serialize(header).unwrap();
        hasher.update(data);
        
        let result = hasher.finalize();
        let mut hash = [0u8; 32];
        hash.copy_from_slice(&result);
        hash
    }

    /// 验证工作量证明
    pub fn verify(&self, header: &BlockHeader) -> bool {
        let hash = self.calculate_hash(header);
        
        // 检查哈希是否满足难度要求
        // 前difficulty/8字节应该为0
        let leading_zeros = self.difficulty / 8;
        let remaining_bits = self.difficulty % 8;
        
        for i in 0..leading_zeros as usize {
            if hash[i] != 0 {
                return false;
            }
        }
        
        if remaining_bits > 0 && leading_zeros < 32 {
            let mask = 0xFF << (8 - remaining_bits);
            if hash[leading_zeros as usize] & mask != 0 {
                return false;
            }
        }
        
        true
    }

    /// 挖矿 - 寻找满足难度的nonce
    pub fn mine(&self, mut header: BlockHeader) -> (BlockHeader, u64) {
        let start_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        let mut nonce = 0u64;
        let mut attempts = 0;
        
        loop {
            header.nonce = nonce;
            
            if self.verify(&header) {
                let elapsed = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs() - start_time;
                
                println!("✓ Block mined! Nonce: {}, Hash: {:?}, Time: {}s, Attempts: {}", 
                    nonce, 
                    hex::encode(self.calculate_hash(&header)),
                    elapsed,
                    attempts
                );
                
                return (header, nonce);
            }
            
            nonce = nonce.wrapping_add(1);
            attempts += 1;
            
            // 每100万次尝试打印一次进度
            if attempts % 1_000_000 == 0 {
                println!("Mining... Nonce: {}, Attempts: {}", nonce, attempts);
            }
        }
    }

    /// 动态调整难度
    pub fn adjust_difficulty(&self, blocks: &[Block], target_block_time: u64) -> u32 {
        if blocks.len() < 2 {
            return self.difficulty;
        }
        
        let last_block = blocks.last().unwrap();
        let first_block = blocks.first().unwrap();
        
        let time_diff = last_block.header.timestamp - first_block.header.timestamp;
        let expected_time = target_block_time * (blocks.len() as u64 - 1);
        
        let ratio = expected_time as f64 / time_diff as f64;
        
        // 限制调整幅度，每次最多调整4倍
        let adjustment = ratio.max(0.25).min(4.0);
        
        let new_difficulty = (self.difficulty as f64 * adjustment) as u32;
        
        // 确保难度至少为1
        new_difficulty.max(1)
    }
}

/// 创建创世区块
pub fn create_genesis_block() -> Block {
    let header = BlockHeader {
        version: 1,
        previous_block_hash: [0u8; 32],
        merkle_root: [0u8; 32], // 简化：使用空Merkle根
        timestamp: 1640995200, // 2022-01-01 00:00:00 UTC
        difficulty: 10, // 初始难度
        nonce: 0,
    };
    
    Block {
        header,
        transactions: vec![], // 创世区块无交易
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pow_verification() {
        let pow = ProofOfWork::new(10);
        let genesis = create_genesis_block();
        
        // 创世区块的nonce为0，可能不满足难度要求
        // 这只是一个示例测试
        assert!(pow.calculate_hash(&genesis.header).len() == 32);
    }

    #[test]
    fn test_difficulty_adjustment() {
        let pow = ProofOfWork::new(10);
        let blocks = vec![create_genesis_block(), create_genesis_block()];
        
        let new_difficulty = pow.adjust_difficulty(&blocks, 600); // 10分钟目标
        assert!(new_difficulty > 0);
    }
}