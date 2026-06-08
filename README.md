# KryoMine (KRYO)

**GPU-mineable cryptocurrency with memory-hard proof of work.**

> ⚠️ **Project Status: Early Development (Alpha v0.1.0)**
> 
> This project is in active development. The blockchain node can mine and
> validate blocks on CPU. GPU mining support is planned but not yet
> implemented. **Testnet not yet launched. No coins have real value.**

## What is KryoMine?

KryoMine is a Proof-of-Work cryptocurrency designed to be mined with GPUs.
It uses a custom memory-hard algorithm (GigaHash) that requires ~256MB of
memory per mining thread, naturally favoring GPUs with their high memory
bandwidth over ASICs and CPUs.

## Key Design Principles

1. **GPU-Friendly Mining** — Memory-hard PoW algorithm (GigaHash) favors
   GPUs through high memory bandwidth requirements
2. **Fair Launch** — No pre-mine, no ICO, no investor allocation.
   All coins are produced through mining.
3. **Fixed Supply** — Maximum 21 million KRYO, with Bitcoin-like halving
   (every 210,000 blocks, approximately every 4 years)
4. **Anti-ASIC** — Large memory requirements make ASIC development
   economically unfavorable

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| Algorithm | GigaHash (custom memory-hard PoW) |
| Max Supply | 21,000,000 KRYO |
| Block Time | 10 minutes (target) |
| Initial Reward | 50 KRYO |
| Halving Interval | 210,000 blocks (~4 years) |
| Memory Requirement | 256 MB per thread |
| Difficulty Adjustment | Every 2016 blocks |

## Current Implementation

The current codebase (`v0.1.0`) provides:

- ✅ Blockchain node with HTTP API
- ✅ CPU mining (GigaHash algorithm, single + multi-threaded)
- ✅ Chain validation and state management
- ✅ Wallet generation
- ✅ Transaction creation and mempool
- ✅ UTXO-based account model

**Not yet implemented:**
- ❌ GPU mining (algorithm supports it, miner not written)
- ❌ P2P networking (node works in standalone mode)
- ❌ Cryptographic transaction signing (placeholder)
- ❌ Smart contract support
- ❌ Block explorer

## Quick Start

### Prerequisites
- Python 3.9+
- No external dependencies required (uses only standard library)

### Install

```bash
git clone https://github.com/personachain001/aethercoin.git
cd aethercoin
```

### Run Tests

```bash
python3 src/cli.py test
```

### Mine (CPU)

```bash
# Single-threaded mining
python3 src/cli.py mine

# Multi-threaded mining (use all CPU cores)
python3 src/cli.py mine --threads 8
```

### Start Node

```bash
python3 src/cli.py node --port 8333
```

API endpoints:
- `GET /stats` — Chain statistics
- `GET /blocks/latest` — Latest block
- `GET /mempool` — Transaction mempool
- `POST /transaction` — Submit transaction
- `POST /mine` — Mine a block

### Create Wallet

```bash
python3 src/cli.py wallet create
```

## Mining Performance

**CPU benchmark** (Apple M1, 8 threads):
- Single thread: ~8,000-100,000 H/s at difficulty 4
- Multi-thread (8 cores): ~60,000-800,000 H/s
- 256MB shared memory buffer (all threads read from same buffer)

**GPU projection:**
- Expected 10-100x speedup due to GDDR memory bandwidth advantage
- GDDR6: 300-1000 GB/s vs CPU DDR5: 50-100 GB/s
- GPU implementation (OpenCL/CUDA) planned for v0.3.0

*Note: GPU mining support requires writing an OpenCL/CUDA implementation
of the GigaHash algorithm. This is planned for a future release.*

## Economic Model

```
Block 0-210,000:     50 KRYO reward
Block 210,001-420,000:  25 KRYO reward
Block 420,001-630,000:  12.5 KRYO reward
... (halves every 210,000 blocks)
```

Total supply asymptotically approaches 21,000,000 KRYO.
Final coins mined around year 2140.

## Project Structure

```
src/
├── blockchain.py     — Core blockchain (block, chain, PoW, validation)
├── miner.py          — Standalone mining module
├── node.py           — HTTP node server
├── wallet.py         — Wallet generation and management
└── cli.py            — CLI interface and self-tests

docs/web/
├── index.html        — Project website
├── explorer/         — Block explorer (planned)
└── wallet/           — Web wallet (planned)
```

## Roadmap

- **v0.2.0** — P2P networking between nodes
- **v0.3.0** — GPU miner (OpenCL/CUDA)
- **v0.4.0** — Transaction signing (cryptography)

*Timeline: No fixed dates. This is an open-source community project.*

## Known Limitations

1. **No P2P network** — Nodes cannot discover or communicate with each other yet
2. **No crypto signing** — Transactions currently use placeholder signatures.
   Real ED25519/ECDSA signing is needed before any real use.
3. **No persistent peers** — Each node operates independently
4. **CPU-only mining** — GPU support requires additional development

## Why Another Cryptocurrency?

Most new cryptocurrency projects are tokens on existing chains with
pre-mines and VC allocations. KryoMine is an experiment in going back to
basics: proof-of-work mining that anyone with a GPU can participate in,
with verifiably fair distribution.

We believe that GPU mining is the most accessible form of cryptocurrency
mining — almost everyone with a gaming PC has the hardware to participate.

## Contributing

This is a community-driven open-source project. Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

Please be honest in your contributions. No fake statistics, no dead links,
no promises of features that don't exist.

## Contact

- **GitHub**: https://github.com/personachain001/aethercoin
- **Email**: personachain001@gmail.com

## License

MIT License — See [LICENSE](LICENSE) file.

---

**KryoMine — Fair mining for everyone.**
