"""
KryoMine Node — HTTP-based blockchain node.

Provides REST API for interacting with the blockchain:
- GET /stats          — Network statistics
- GET /blocks/latest  — Latest block
- GET /blocks/<hash>  — Block by hash
- POST /transaction   — Submit transaction
- POST /mine          — Mine a block

Usage:
    python node.py [--port 8333]
"""

import json
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from blockchain import Blockchain, Transaction
from wallet import Wallet
import threading


class NodeAPI(BaseHTTPRequestHandler):
    blockchain: Blockchain = None
    wallet: Wallet = None

    def do_GET(self):
        if self.path == "/stats":
            self._json_response(200, self.blockchain.get_stats())
        elif self.path == "/blocks/latest":
            block = self.blockchain.get_latest_block()
            self._json_response(200, block.to_dict())
        elif self.path.startswith("/blocks/"):
            block_hash = self.path.split("/")[-1]
            for block in self.blockchain.chain:
                if block.hash == block_hash:
                    self._json_response(200, block.to_dict())
                    return
            self._json_response(404, {"error": "Block not found"})
        elif self.path == "/mempool":
            txs = [t.to_dict() for t in self.blockchain.mempool]
            self._json_response(200, {"count": len(txs), "transactions": txs})
        elif self.path.startswith("/balance/"):
            address = self.path.split("/")[-1]
            balance = self.blockchain.get_balance(address)
            self._json_response(200, {"address": address, "balance": balance})
        else:
            self._json_response(404, {"error": "Not found", "path": self.path})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._json_response(400, {"error": "Invalid JSON"})
            return

        if self.path == "/transaction":
            if not all(k in data for k in ("sender", "recipient", "amount")):
                self._json_response(400, {"error": "Missing fields"})
                return

            tx = Transaction(
                sender=data["sender"],
                recipient=data["recipient"],
                amount=int(data["amount"]),
            )
            success = self.blockchain.add_transaction(tx)
            if success:
                self._json_response(200, {
                    "status": "accepted",
                    "tx_hash": tx.hash(),
                })
            else:
                self._json_response(400, {
                    "error": "Invalid transaction (insufficient balance?)"
                })

        elif self.path == "/mine":
            # Run mining in a separate thread to avoid blocking
            address = data.get("address", self.wallet.get_address())
            if not address:
                self._json_response(400, {"error": "No miner address provided"})
                return

            print(f"\n⛏ Mining triggered by {address}...")
            # Start mining in background thread
            def mine_async():
                block = self.blockchain.mine_block(address)
                if block:
                    print(f"✅ Block mined: {block.hash[:16]}...")
            
            threading.Thread(target=mine_async, daemon=True).start()
            self._json_response(202, {
                "status": "mining_started",
                "message": "Mining started in background. Check /stats for results."
            })

        else:
            self._json_response(404, {"error": "Not found"})

    def _json_response(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        """Suppress default logging, use cleaner format."""
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KryoMine Node")
    parser.add_argument("--port", type=int, default=8333,
                        help="Node port (default: 8333)")
    parser.add_argument("--bind", default="127.0.0.1",
                        help="Bind address (default: 127.0.0.1, use 0.0.0.0 for public)")
    parser.add_argument("--data-dir", default="~/.kryomine",
                        help="Data directory (default: ~/.kryomine)")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════╗
║       KryoMine Node v0.1.0          ║
║   GPU-Mineable Cryptocurrency       ║
╚══════════════════════════════════════╝
""")

    # Initialize
    NodeAPI.blockchain = Blockchain(data_dir=args.data_dir)
    NodeAPI.wallet = Wallet(wallet_dir=args.data_dir)

    # Auto-create wallet if doesn't exist
    if not NodeAPI.wallet.get_address():
        addr = NodeAPI.wallet.create()
        print(f"📝 New wallet created: {addr[:16]}...")

    stats = NodeAPI.blockchain.get_stats()
    print(f"📊 Chain height: {stats['height']}")
    print(f"💰 Total supply: {stats['total_supply']} KRYO / {stats['max_supply']} KRYO max")
    print(f"🔧 Difficulty: {stats['difficulty']}")
    print(f"🌐 Node running on http://localhost:{args.port}")
    print(f"\nAPI endpoints:")
    print(f"  GET  /stats         — Chain statistics")
    print(f"  GET  /blocks/latest — Latest block")
    print(f"  GET  /mempool       — Transaction mempool")
    print(f"  POST /transaction   — Submit transaction")
    print(f"  POST /mine          — Mine a block")
    print()

    server = HTTPServer((args.bind, args.port), NodeAPI)
    print(f"🌐 Node running on http://{args.bind}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Node stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
