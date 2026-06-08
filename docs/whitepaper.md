# KryoMine: A GPU-Mineable Cryptocurrency with Memory-Hard Proof of Work

**Whitepaper v0.1.0 — June 2026**

---

## Abstract

KryoMine (KRYO) is a Proof-of-Work cryptocurrency designed for GPU mining.
It uses a custom memory-hard algorithm called GigaHash that requires
approximately 256MB of memory per mining instance. This memory requirement
naturally favors Graphics Processing Units (GPUs) due to their high memory
bandwidth (300-1000 GB/s for GDDR6) compared to CPUs (50-100 GB/s for DDR4),
while making Application-Specific Integrated Circuit (ASIC) development
economically unfavorable. The project follows a fair launch model with no
pre-mine, no initial coin offering, and a fixed maximum supply of 21 million
coins.

---

## 1. Introduction

### 1.1 The Problem

Cryptocurrency mining has become increasingly centralized. Bitcoin mining
is dominated by ASIC manufacturers and large mining farms. Even GPU-mineable
coins face centralization through mining pools and ASIC development.

New cryptocurrency projects typically launch with:
- Pre-mined allocations for founders and investors
- Token sales that favor early participants
- Complex tokenomics designed for speculation rather than utility

### 1.2 Our Approach

KryoMine aims to return to first principles:
- **Proof of Work** — The most battle-tested consensus mechanism
- **GPU Mining** — Widely accessible hardware (gaming PCs)
- **Memory-Hard Algorithm** — ASIC-resistant by design
- **Fair Launch** — No pre-mine, coins only from mining
- **Fixed Supply** — 21 million KRYO maximum

---

## 2. Technical Architecture

### 2.1 GigaHash Algorithm

GigaHash is a memory-hard proof-of-work algorithm designed specifically
for GPU mining. It is inspired by Ethash (Ethereum's original PoW) and
KawPow (Ravencoin's algorithm).

#### Algorithm Steps

1. **Seed Generation**: The block header (excluding nonce) is hashed with
   SHA-512 to produce a 64-byte seed.

2. **Memory Buffer Fill**: The seed is used to deterministically fill a
   memory buffer of configurable size (default: 256MB). The buffer is
   filled using repeated SHA-512 hashing with sequential counter mixing.

3. **Mining Loop**: For each nonce attempt:
   a. Three pseudo-random positions are selected from the memory buffer
      using the nonce and seed as position selectors
   b. Data from these positions is mixed with the nonce
   c. The mixed data is hashed with SHA-256
   d. If the resulting hash is below the difficulty target, the block
      is valid

4. **Verification**: To verify a mined block, the verifier re-fills the
   memory buffer using the same seed and checks the hash with the claimed
   nonce.

#### Why Memory-Hard?

Memory-hard algorithms require miners to store and access large amounts of
data. This design choice has several effects:

| Hardware | Memory Bandwidth | Relative Performance |
|----------|-----------------|---------------------|
| High-end GPU (RTX 4090) | ~1000 GB/s | 10-20x |
| Mid-range GPU (RTX 3060) | ~360 GB/s | 3-7x |
| High-end CPU (DDR5) | ~70 GB/s | 1x (baseline) |
| ASIC (custom) | Variable | Expensive to design for large memory |

The key insight: **memory bandwidth, not computation speed, is the bottleneck**.
ASICs can't bypass this without expensive high-bandwidth memory (HBM), which
makes their development cost-prohibitive compared to using commodity GPUs.

### 2.2 Block Structure

```
Block:
├── BlockHeader
│   ├── version: uint32
│   ├── previous_hash: [32]byte
│   ├── merkle_root: [32]byte
│   ├── timestamp: uint64 (Unix seconds)
│   ├── difficulty: uint64
│   └── nonce: uint64
├── Transactions[]
│   ├── sender: address
│   ├── recipient: address
│   ├── amount: uint64 (satoshis)
│   └── signature: bytes
└── hash: [32]byte
```

### 2.3 Consensus Rules

1. **Longest Chain Rule**: The valid chain with the most accumulated work
   (difficulty) is the canonical chain.

2. **Block Validation**:
   - Previous hash must match the tip of the current chain
   - PoW must be valid (hash < target)
   - Timestamp must be within 2 hours of network time
   - All transactions must be valid

3. **Difficulty Adjustment**: Every 2016 blocks, the difficulty is
   recalculated to target a 10-minute block time:
   ```
   new_difficulty = old_difficulty * (expected_time / actual_time)
   ```

---

## 3. Economic Model

### 3.1 Supply Schedule

KryoMine follows Bitcoin's proven supply schedule:

| Block Range | Reward (KRYO) |
|-------------|---------------|
| 0 - 210,000 | 50.0 |
| 210,001 - 420,000 | 25.0 |
| 420,001 - 630,000 | 12.5 |
| 630,001 - 840,000 | 6.25 |
| ... | ... |

Total supply asymptotically approaches 21,000,000 KRYO.

### 3.2 Fair Launch Guarantees

- **No Pre-mine**: The genesis block contains only a single unspendable
  coinbase transaction to a burn address.
- **No ICO/Token Sale**: No tokens were sold before mining began.
- **No Developer Allocation**: All developers mine on the same terms as
  everyone else.
- **Verifiable**: Anyone can verify the genesis block and initial supply
  by inspecting the open-source code and chain data.

### 3.3 Why 21 Million?

We chose Bitcoin's supply parameters for simplicity and familiarity.
21 million coins with 8 decimal places (10^8 satoshis) provides
sufficient divisibility for any use case, while the halving schedule
ensures predictable, decreasing inflation.

---

## 4. Current Status and Limitations

### 4.1 What Works (v0.1.0)

- Blockchain node with HTTP API
- CPU mining with GigaHash algorithm
- Block validation and chain state management
- Simple wallet generation
- Transaction mempool
- Self-test suite

### 4.2 Known Limitations

1. **No P2P Network**: The current node operates in standalone mode.
   P2P peer discovery and block propagation are planned for v0.2.0.

2. **No Cryptographic Signatures**: Transactions currently use placeholder
   signatures. ED25519 or ECDSA signing will be implemented before any
   testnet launch.

3. **CPU-Only Mining**: While the algorithm design favors GPUs, the
   current implementation only supports CPU mining. GPU mining requires
   an OpenCL or CUDA implementation.

4. **No Testnet**: There is no public testnet yet. All testing is done
   locally with a single node.

### 4.3 Security Considerations

This code has NOT been audited by a third party. It should NOT be used
with real value until:
1. Cryptographic signing is implemented
2. P2P networking is complete
3. A security audit has been performed
4. A public testnet has been running for an extended period

---

## 5. Comparison with Existing Projects

| Feature | KryoMine | Monero | Ravencoin | Bitcoin |
|---------|----------|--------|-----------|---------|
| Algorithm | GigaHash (custom) | RandomX | KawPow | SHA-256 |
| Mining | GPU (planned) | CPU only | GPU | ASIC |
| Max Supply | 21M | ~18.4M + tail | 21B | 21M |
| Privacy | Planned | Default | None | None |
| Fair Launch | Yes | No (contested) | Yes | Yes |
| Pre-mine | None | None | None | None |

---

## 6. Roadmap

### v0.2.0 — Networking
- P2P peer discovery (Kademlia DHT)
- Block and transaction propagation
- Node synchronization

### v0.3.0 — GPU Mining
- OpenCL implementation of GigaHash
- CUDA implementation (NVIDIA)
- Mining pool protocol

### v0.4.0 — Security
- ED25519 transaction signing
- Address encoding (Bech32-style)
- UTXO set commitments

*No specific dates are committed. Development pace depends on community
contributions and maintainer availability.*

---

## 7. Conclusion

KryoMine is an experiment in fair cryptocurrency distribution through
GPU mining. The memory-hard GigaHash algorithm is designed to keep mining
accessible to anyone with a gaming PC while resisting ASIC centralization.

This is early-stage, open-source software. It is not an investment product.
The code is provided as-is, under the MIT license, for anyone to study,
use, or improve.

---

## References

1. Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.
2. Ethereum Foundation. Ethash Design Rationale.
3. Ravencoin. KawPow algorithm specification.
4. RandomX. The RandomX Proof of Work Algorithm.
