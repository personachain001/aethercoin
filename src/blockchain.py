"""
KryoMine (KRYO) — Core Blockchain Implementation

A GPU-mineable cryptocurrency with memory-hard proof of work.
Designed for fair launch — no pre-mine, no ICO.

This is a functional implementation. The mining algorithm
(GigaHash) is designed to be GPU-friendly through its
large memory requirement, similar to Ethash.
"""

import hashlib
import json
import struct
import threading
import time
from dataclasses import dataclass, field
from typing import Optional


# === Configuration ===
MAX_SUPPLY = 21_000_000        # Maximum coin supply (in whole KRYO)
INITIAL_BLOCK_REWARD = 50.0    # Initial mining reward
HALVING_INTERVAL = 210_000     # Blocks between halvings
TARGET_BLOCK_TIME = 600        # Target seconds per block (10 minutes)
DIFFICULTY_ADJUST_INTERVAL = 2016  # Blocks between difficulty adjustments
MEMORY_SIZE_MB = 256           # Memory requirement for PoW (MB)
COIN_DECIMALS = 8              # 1 KRYO = 10^8 satoshis


@dataclass
class Transaction:
    """A single transaction on the blockchain."""
    sender: str
    recipient: str
    amount: int         # In satoshis (10^-8 KRYO)
    timestamp: float = field(default_factory=time.time)
    signature: str = ""  # Placeholder for future crypto signing

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(**data)

    def hash(self) -> str:
        """Hash this transaction."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class BlockHeader:
    """Block header without transactions."""
    version: int = 1
    previous_hash: str = ""
    merkle_root: str = ""
    timestamp: float = 0.0
    difficulty: int = 1
    nonce: int = 0

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
        }

    def hash(self) -> str:
        """Hash the block header."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class Block:
    """A complete block with header and transactions."""
    header: BlockHeader = field(default_factory=BlockHeader)
    transactions: list = field(default_factory=list)
    hash: str = ""

    def compute_merkle_root(self) -> str:
        """Compute Merkle root from transactions."""
        if not self.transactions:
            return hashlib.sha256(b"").hexdigest()

        tx_hashes = [t.hash() if hasattr(t, 'hash') else hashlib.sha256(
            json.dumps(t.to_dict() if hasattr(t, 'to_dict') else str(t),
                       sort_keys=True).encode()).hexdigest()
                     for t in self.transactions]

        if len(tx_hashes) == 1:
            return tx_hashes[0]

        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hashes.append(hashlib.sha256(
                    combined.encode()).hexdigest())
            tx_hashes = new_hashes

        return tx_hashes[0]

    def compute_hash(self) -> str:
        """Compute the block hash."""
        self.header.merkle_root = self.compute_merkle_root()
        return self.header.hash()

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "transactions": [t.to_dict() if hasattr(t, 'to_dict')
                             else t for t in self.transactions],
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        header = BlockHeader(**data["header"])
        transactions = []
        for t in data.get("transactions", []):
            if isinstance(t, dict):
                transactions.append(Transaction.from_dict(t))
            else:
                transactions.append(t)
        block = cls(header=header, transactions=transactions)
        block.hash = data.get("hash", "")
        return block


def compute_block_reward(height: int) -> int:
    """Compute mining reward for a given block height.

    Returns amount in satoshis (10^-8 KRYO).
    Follows Bitcoin-like halving: reward halves every 210,000 blocks.
    """
    halvings = height // HALVING_INTERVAL
    if halvings >= 64:
        return 0  # All coins mined
    reward = int(INITIAL_BLOCK_REWARD * (10 ** COIN_DECIMALS))
    reward >>= halvings  # Integer division by 2^halvings
    return reward


class Blockchain:
    """The main blockchain database."""

    def __init__(self, data_dir: str = "~/.kryomine"):
        import os
        self.data_dir = os.path.expanduser(data_dir)
        self.chain_file = os.path.join(self.data_dir, "chain.json")
        self.mempool_file = os.path.join(self.data_dir, "mempool.json")
        self.utxo_file = os.path.join(self.data_dir, "utxo.json")

        os.makedirs(self.data_dir, exist_ok=True)

        self.chain: list[Block] = []
        self.mempool: list[Transaction] = []
        self.utxo_set: dict[str, int] = {}  # address -> balance in satoshis
        self._mine_lock = threading.Lock()

        self._load_chain()

    def _load_chain(self):
        """Load or create the blockchain from disk."""
        import os
        if os.path.exists(self.chain_file):
            with open(self.chain_file, "r") as f:
                data = json.load(f)
            self.chain = [Block.from_dict(b) for b in data]
            self._rebuild_utxo_set()
        else:
            self.chain = [self._create_genesis_block()]
            self._save_chain()
            self._rebuild_utxo_set()  # Ensure genesis coinbase is in UTXO

        if os.path.exists(self.mempool_file):
            with open(self.mempool_file, "r") as f:
                data = json.load(f)
            self.mempool = [Transaction.from_dict(t) for t in data]

    def _save_chain(self):
        """Save blockchain to disk."""
        data = [b.to_dict() for b in self.chain]
        with open(self.chain_file, "w") as f:
            json.dump(data, f, indent=2)

    def _save_mempool(self):
        """Save mempool to disk."""
        data = [t.to_dict() for t in self.mempool]
        with open(self.mempool_file, "w") as f:
            json.dump(data, f, indent=2)

    def _create_genesis_block(self) -> Block:
        """Create the genesis (first) block."""
        header = BlockHeader(
            version=1,
            previous_hash="0" * 64,
            timestamp=time.time(),
            difficulty=1,
        )
        coinbase = Transaction(
            sender="0" * 64,  # Genesis coinbase
            recipient="0000000000000000000000000000000000000000000000000000000000000001",
            amount=compute_block_reward(0),
            timestamp=header.timestamp,
        )
        block = Block(header=header, transactions=[coinbase])
        block.hash = block.compute_hash()
        return block

    def _rebuild_utxo_set(self):
        """Rebuild UTXO set from chain (simplified: account-based)."""
        self.utxo_set = {}
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender != "0" * 64:  # Not coinbase
                    self.utxo_set[tx.sender] = self.utxo_set.get(
                        tx.sender, 0) - tx.amount
                self.utxo_set[tx.recipient] = self.utxo_set.get(
                    tx.recipient, 0) + tx.amount

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def get_height(self) -> int:
        return len(self.chain)

    def get_balance(self, address: str) -> int:
        """Get balance in satoshis."""
        return self.utxo_set.get(address, 0)

    def get_total_supply(self) -> float:
        """Get total mined supply in whole KRYO."""
        total = sum(compute_block_reward(i) for i in range(len(self.chain)))
        return total / (10 ** COIN_DECIMALS)

    def add_transaction(self, tx: Transaction) -> bool:
        """Add a transaction to the mempool, with double-spend prevention."""
        if tx.amount <= 0:
            return False
        if tx.sender == "0" * 64:
            return False  # Coinbase transactions are created during mining

        # Check on-chain balance minus all pending mempool outbound amounts
        on_chain = self.utxo_set.get(tx.sender, 0)
        pending_out = sum(t.amount for t in self.mempool
                         if t.sender == tx.sender)
        available = on_chain - pending_out

        if available < tx.amount:
            return False

        self.mempool.append(tx)
        self._save_mempool()
        return True

    def mine_block(self, miner_address: str) -> Optional[Block]:
        """Mine a new block and add it to the chain."""
        # Prevent concurrent mining
        if not self._mine_lock.acquire(blocking=False):
            print("Mining already in progress, skipping.")
            return None
        try:
            latest = self.get_latest_block()

            # Create new block header
            header = BlockHeader(
                version=1,
                previous_hash=latest.hash,
                timestamp=time.time(),
                difficulty=self._get_current_difficulty(),
            )

            # Collect transactions from mempool
            transactions = []
            # Coinbase transaction
            reward = compute_block_reward(self.get_height())
            coinbase = Transaction(
                sender="0" * 64,
                recipient=miner_address,
                amount=reward,
            )
            transactions.append(coinbase)

            # Add mempool transactions (with double-spend prevention)
            temp_balances = dict(self.utxo_set)  # Track balances during tx selection
            for tx in self.mempool[:100]:  # Max 100 tx per block
                if tx.sender != "0" * 64:
                    available = temp_balances.get(tx.sender, 0)
                    if available >= tx.amount:
                        transactions.append(tx)
                        temp_balances[tx.sender] = available - tx.amount
                else:
                    transactions.append(tx)

            block = Block(header=header, transactions=transactions)
            block.header.merkle_root = block.compute_merkle_root()

            # Mine (perform proof of work)
            print(f"Mining block #{self.get_height()} at difficulty {header.difficulty}...")
            mined = mine_gigahash(block.header)
            if mined is None:
                print("Mining failed!")
                return None

            block.header = mined

            block.hash = block.compute_hash()

            # Add to chain
            self.chain.append(block)

            # Remove processed transactions from mempool
            tx_ids = {t.hash() for t in transactions if t.sender != "0" * 64}
            self.mempool = [t for t in self.mempool if t.hash() not in tx_ids]

            # Update UTXO set
            for tx in transactions:
                if tx.sender != "0" * 64:
                    self.utxo_set[tx.sender] = self.utxo_set.get(
                        tx.sender, 0) - tx.amount
                self.utxo_set[tx.recipient] = self.utxo_set.get(
                    tx.recipient, 0) + tx.amount

            self._save_chain()
            self._save_mempool()

            return block
        finally:
            self._mine_lock.release()

    def _get_current_difficulty(self) -> int:
        """Calculate current mining difficulty."""
        height = self.get_height()
        if height < 2:
            return 4  # Initial difficulty (easy for testing)

        if height % DIFFICULTY_ADJUST_INTERVAL == 0 and height >= DIFFICULTY_ADJUST_INTERVAL:
            # Calculate actual time for last interval
            interval_start = self.chain[height - DIFFICULTY_ADJUST_INTERVAL]
            interval_end = self.chain[-1]
            actual_time = interval_end.header.timestamp - \
                interval_start.header.timestamp
            expected_time = DIFFICULTY_ADJUST_INTERVAL * TARGET_BLOCK_TIME

            # Adjust difficulty (with 4x bounds, same as Bitcoin)
            if actual_time > 0:
                ratio = expected_time / actual_time
                # Clamp ratio to [0.25, 4.0] to prevent extreme difficulty swings
                ratio = max(0.25, min(4.0, ratio))
                new_diff = int(self.chain[-1].header.difficulty * ratio)
                return max(1, new_diff)

        return self.chain[-1].header.difficulty

    def is_valid_chain(self) -> bool:
        """Validate the entire chain, including genesis block."""
        # Validate genesis block
        genesis = self.chain[0]
        if genesis.header.previous_hash != "0" * 64:
            return False
        if genesis.hash != genesis.compute_hash():
            return False

        for i in range(1, len(self.chain)):
            block = self.chain[i]
            prev_block = self.chain[i - 1]

            # Check previous hash links
            if block.header.previous_hash != prev_block.hash:
                return False

            # Verify block hash
            if block.hash != block.compute_hash():
                return False

            # Verify PoW
            if not verify_gigahash(block.header):
                return False

        return True

    def get_stats(self) -> dict:
        """Get chain statistics."""
        return {
            "height": self.get_height(),
            "latest_hash": self.get_latest_block().hash[:16] + "...",
            "total_supply": self.get_total_supply(),
            "max_supply": MAX_SUPPLY,
            "difficulty": self._get_current_difficulty(),
            "mempool_size": len(self.mempool),
            "last_block_time": self.get_latest_block().header.timestamp,
        }


# === Mining Algorithm: GigaHash ===
#
# GigaHash is a memory-hard PoW algorithm designed to be GPU-friendly.
# It requires a large memory buffer (~256 MB by default) that is filled
# and repeatedly hashed. GPUs excel at this due to their massive memory
# bandwidth (hundreds of GB/s vs CPU's tens of GB/s).
#
# Algorithm:
# 1. Hash the block header to create a seed
# 2. Fill a memory buffer (MEMORY_SIZE_MB) with pseudo-random data derived
#    from the seed
# 3. In each mining attempt:
#    a. Pick random positions in the buffer
#    b. Mix data from those positions with the current nonce
#    c. Compute final hash
#    d. Check if hash meets difficulty target
#
# The large memory requirement makes ASICs expensive (they'd need high
# bandwidth memory), while GPUs handle it naturally through GDDR/HBM.

def _fill_memory_buffer(seed: bytes, size_mb: int) -> bytes:
    """Fill a memory buffer with pseudo-random data based on seed.

    This creates the large memory requirement that makes the algorithm
    GPU-friendly (GPU memory bandwidth) but ASIC-expensive.
    """
    buffer = bytearray()
    hasher = hashlib.sha512()
    data = seed
    target_bytes = size_mb * 1024 * 1024

    while len(buffer) < target_bytes:
        hasher.update(data)
        data = hasher.digest() + struct.pack(">Q", len(buffer))
        buffer.extend(data)
        hasher = hashlib.sha512(data)

    return bytes(buffer[:target_bytes])


def _hash_block_header(header: BlockHeader) -> bytes:
    """Hash block header to get a deterministic 64-byte seed.
    
    Excludes 'nonce' from the hash so that the memory buffer seed is
    consistent between mining (nonce changes) and verification (nonce is fixed).
    """
    header_dict = header.to_dict()
    # Remove nonce so seed is consistent for mining and verification
    saved_nonce = header_dict.pop("nonce", None)
    data = json.dumps(header_dict, sort_keys=True).encode()
    header_dict["nonce"] = saved_nonce  # Restore
    return hashlib.sha512(data).digest()


def mine_gigahash(header: BlockHeader, memory_mb: int = MEMORY_SIZE_MB) -> Optional[BlockHeader]:
    """Mine a block using the GigaHash algorithm.

    Returns the header with a valid nonce, or None if mining failed.
    """
    from math import log2

    seed = _hash_block_header(header)

    # Fill memory buffer (this is done once before mining loop)
    print(f"  Filling {memory_mb}MB memory buffer...", end=" ", flush=True)
    buffer = _fill_memory_buffer(seed, memory_mb)
    print("done.")

    # Calculate target: smaller target = harder
    target_bits = 256 - int(log2(header.difficulty)) if header.difficulty > 0 else 256
    target = (1 << target_bits) - 1 if target_bits > 0 else 1

    print(f"  Mining... (difficulty={header.difficulty})", flush=True)

    max_nonce = 2 ** 48  # Reasonable nonce space
    start_time = time.time()
    buffer_len = len(buffer)

    for nonce in range(max_nonce):
        # Pick multiple positions in the memory buffer
        # The positions depend on the nonce and seed for determinism
        pos1 = (nonce * 7 + 13) % (buffer_len - 64)
        pos2 = (nonce * 31 + 97) % (buffer_len - 64)
        pos3 = ((nonce ^ 0x5555) * 127 + 491) % (buffer_len - 64)

        # Mix data from buffer positions with nonce
        mixed = (buffer[pos1:pos1 + 64] +
                 buffer[pos2:pos2 + 32] +
                 buffer[pos3:pos3 + 32] +
                 struct.pack(">Q", nonce))

        # Final hash
        result = hashlib.sha256(mixed).digest()
        result_int = int.from_bytes(result, "big")

        if result_int <= target:
            elapsed = time.time() - start_time
            header.nonce = nonce
            print(f"  ✓ Block mined! Nonce={nonce}, {elapsed:.1f}s, "
                  f"hashrate: {nonce / elapsed:.0f} H/s (CPU)")
            return header

        # Progress indicator
        if nonce % 100000 == 0 and nonce > 0:
            elapsed = time.time() - start_time
            if elapsed > 0:
                print(f"  ... {nonce} attempts, "
                      f"{nonce / elapsed:.0f} H/s", flush=True)

        # Timeout: if mining takes too long, return None
        if time.time() - start_time > 300:  # 5 minutes timeout
            print("  ✗ Mining timed out after 5 minutes")
            return None

    return None


def verify_gigahash(header: BlockHeader, memory_mb: int = MEMORY_SIZE_MB) -> bool:
    """Verify that a block header's PoW is valid."""
    from math import log2

    seed = _hash_block_header(header)
    buffer = _fill_memory_buffer(seed, memory_mb)

    target_bits = 256 - int(log2(header.difficulty)) if header.difficulty > 0 else 256
    target = (1 << target_bits) - 1 if target_bits > 0 else 1

    buffer_len = len(buffer)
    nonce = header.nonce

    pos1 = (nonce * 7 + 13) % (buffer_len - 64)
    pos2 = (nonce * 31 + 97) % (buffer_len - 64)
    pos3 = ((nonce ^ 0x5555) * 127 + 491) % (buffer_len - 64)

    mixed = (buffer[pos1:pos1 + 64] +
             buffer[pos2:pos2 + 32] +
             buffer[pos3:pos3 + 32] +
             struct.pack(">Q", nonce))

    result = hashlib.sha256(mixed).digest()
    result_int = int.from_bytes(result, "big")

    return result_int <= target
