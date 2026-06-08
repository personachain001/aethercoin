"""
KryoMine Miner — Standalone mining module.

Usage:
    python miner.py --address YOUR_ADDRESS [--threads N]
"""

import argparse
import hashlib
import struct
import time
from blockchain import (
    BlockHeader, mine_gigahash, _hash_block_header, MEMORY_SIZE_MB
)


def create_mining_header(previous_hash: str, difficulty: int) -> BlockHeader:
    """Create a block header for mining."""
    return BlockHeader(
        version=1,
        previous_hash=previous_hash,
        timestamp=time.time(),
        difficulty=difficulty,
    )


def main():
    parser = argparse.ArgumentParser(description="KryoMine Miner")
    parser.add_argument("--address", required=True, help="Mining reward address")
    parser.add_argument("--memory", type=int, default=MEMORY_SIZE_MB,
                        help=f"Memory buffer size in MB (default: {MEMORY_SIZE_MB})")
    args = parser.parse_args()

    # For standalone mining demo
    header = create_mining_header(
        previous_hash="0" * 64,
        difficulty=4  # Low difficulty for demo
    )

    print(f"KryoMine Miner v0.1.0")
    print(f"Mining to: {args.address}")
    print(f"Memory buffer: {args.memory}MB")
    print(f"Difficulty: {header.difficulty}")
    print()

    result = mine_gigahash(header, memory_mb=args.memory)
    if result:
        result.hash = result.hash if hasattr(result, 'hash') and result.hash else result.compute_hash()
        print(f"\n✅ Block mined successfully!")
        print(f"   Nonce: {result.nonce}")
        print(f"   Block hash: {result.hash()}")
        print(f"   Hash: {_hash_block_header(result).hex()}")
    else:
        print("\n❌ Mining failed")


if __name__ == "__main__":
    main()
