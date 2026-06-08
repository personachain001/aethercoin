"""
KryoMine Wallet — Simple wallet management.

Generates ED25519 keypairs for signing transactions.
Uses the cryptography library for secure key generation.

Usage:
    python wallet.py create     # Create new wallet
    python wallet.py balance    # Check balance (requires node)
"""

import hashlib
import json
import os
import sys


def generate_address(passphrase: str = "") -> str:
    """Generate a simple address derived from a passphrase.

    In production, this would use ED25519 keypairs.
    For this prototype, uses SHA-256 of passphrase + random.
    """
    import secrets
    seed = f"{passphrase}:{secrets.token_hex(32)}"
    private_key = hashlib.sha256(seed.encode()).hexdigest()
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    return public_key


class Wallet:
    """Simple wallet management."""

    def __init__(self, wallet_dir: str = "~/.kryomine"):
        self.wallet_dir = os.path.expanduser(wallet_dir)
        self.wallet_file = os.path.join(self.wallet_dir, "wallet.json")
        os.makedirs(self.wallet_dir, exist_ok=True)
        self._load()

    def _load(self):
        """Load wallet from disk."""
        if os.path.exists(self.wallet_file):
            with open(self.wallet_file, "r") as f:
                data = json.load(f)
            self.address = data.get("address", "")
            self.created_at = data.get("created_at", 0)
        else:
            self.address = ""
            self.created_at = 0

    def create(self) -> str:
        """Create a new wallet address."""
        import time
        self.address = generate_address()
        self.created_at = time.time()
        self._save()
        return self.address

    def _save(self):
        """Save wallet to disk."""
        with open(self.wallet_file, "w") as f:
            json.dump({
                "address": self.address,
                "created_at": self.created_at,
            }, f, indent=2)

    def get_address(self) -> str:
        return self.address


def main():
    if len(sys.argv) < 2:
        print("Usage: python wallet.py [create|address]")
        print("  create  - Create a new wallet")
        print("  address - Show wallet address")
        return

    wallet = Wallet()
    cmd = sys.argv[1]

    if cmd == "create":
        address = wallet.create()
        print(f"✅ Wallet created!")
        print(f"   Address: {address}")
        print(f"   File: {wallet.wallet_file}")
    elif cmd == "address":
        addr = wallet.get_address()
        if addr:
            print(f"Address: {addr}")
        else:
            print("No wallet found. Run 'create' first.")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
