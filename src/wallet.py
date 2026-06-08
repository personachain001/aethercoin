"""
KryoMine Wallet — ED25519 key management and transaction signing.

Generates ED25519 keypairs for cryptographic transaction signing.
Uses the cryptography library for secure key generation.

Usage:
    python wallet.py create     # Create new wallet
    python wallet.py address    # Show wallet address
"""

import hashlib
import json
import os
import sys
import base64

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False
    print("WARNING: cryptography library not installed. Install with:")
    print("  pip install cryptography")
    print("Transaction signing will NOT work without it.")


class Wallet:
    """ED25519 wallet management."""

    def __init__(self, wallet_dir: str = "~/.kryomine"):
        self.wallet_dir = os.path.expanduser(wallet_dir)
        self.wallet_file = os.path.join(self.wallet_dir, "wallet.json")
        os.makedirs(self.wallet_dir, exist_ok=True)
        self.private_key_bytes: bytes = b""
        self.public_key_bytes: bytes = b""
        self.address: str = ""
        self.created_at: float = 0.0
        self._load()

    def _load(self):
        """Load wallet from disk."""
        if os.path.exists(self.wallet_file):
            with open(self.wallet_file, "r") as f:
                data = json.load(f)
            self.address = data.get("address", "")
            self.created_at = data.get("created_at", 0)
            priv_b64 = data.get("private_key", "")
            if priv_b64:
                self.private_key_bytes = base64.b64decode(priv_b64)
                self.public_key_bytes = base64.b64decode(
                    data.get("public_key", ""))
        else:
            self.address = ""
            self.created_at = 0.0

    def create(self, passphrase: str = "") -> str:
        """Create a new ED25519 wallet and return the address."""
        import time

        if not _HAS_CRYPTO:
            # Fallback: SHA-256 based address (no signing capability)
            import secrets
            seed = f"{passphrase}:{secrets.token_hex(32)}"
            self.address = hashlib.sha256(seed.encode()).hexdigest()
            self.created_at = time.time()
            self._save()
            print("WARNING: cryptography not installed, using SHA-256 fallback.")
            print("Install 'cryptography' for ED25519 signing support.")
            return self.address

        # Generate ED25519 keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Serialize keys
        self.private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        # Address = SHA-256 of public key (64 char hex)
        self.address = hashlib.sha256(self.public_key_bytes).hexdigest()
        self.created_at = time.time()
        self._save()
        return self.address

    def _save(self):
        """Save wallet to disk. Private key is base64-encoded."""
        data = {
            "address": self.address,
            "created_at": self.created_at,
        }
        if self.private_key_bytes:
            data["private_key"] = base64.b64encode(
                self.private_key_bytes).decode()
            data["public_key"] = base64.b64encode(
                self.public_key_bytes).decode()
        with open(self.wallet_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_address(self) -> str:
        return self.address

    def sign(self, message: bytes) -> bytes:
        """Sign a message with the private key. Returns 64-byte signature."""
        if not _HAS_CRYPTO or not self.private_key_bytes:
            raise RuntimeError(
                "Cannot sign: no private key or cryptography not installed")
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
            self.private_key_bytes)
        return private_key.sign(message)

    def verify(self, message: bytes, signature: bytes,
               public_key_bytes: bytes) -> bool:
        """Verify a signature against a public key."""
        if not _HAS_CRYPTO:
            return False
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(
                public_key_bytes)
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False


def get_public_key_from_address(address: str, chain_dir: str = "~/.kryomine"
                                ) -> bytes:
    """Given an address, try to find the corresponding public key."""
    wallet_dir = os.path.expanduser(chain_dir)
    wallet_file = os.path.join(wallet_dir, "wallet.json")
    if os.path.exists(wallet_file):
        with open(wallet_file, "r") as f:
            data = json.load(f)
        if data.get("address") == address:
            pub_b64 = data.get("public_key", "")
            if pub_b64:
                return base64.b64decode(pub_b64)
    return b""


def main():
    if len(sys.argv) < 2:
        print("KryoMine Wallet v0.2.0")
        print(f"  ED25519 signing: {'✅ available' if _HAS_CRYPTO else '❌ unavailable'}")
        print()
        print("Commands:")
        print("  create   - Create a new wallet")
        print("  address  - Show wallet address")
        return

    wallet = Wallet()
    cmd = sys.argv[1]

    if cmd == "create":
        address = wallet.create()
        print(f"✅ Wallet created!")
        print(f"   Address: {address}")
        print(f"   Signing: {'ED25519' if wallet.private_key_bytes else 'SHA-256 (fallback)'}")
        print(f"   File: {wallet.wallet_file}")
    elif cmd == "address":
        addr = wallet.get_address()
        if addr:
            print(f"Address: {addr}")
            print(f"Signing: {'ED25519' if wallet.private_key_bytes else 'SHA-256 (fallback)'}")
        else:
            print("No wallet found. Run 'create' first.")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
