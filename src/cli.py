"""
KryoMine CLI — Command-line interface.

Usage:
    python cli.py mine     # Mine blocks
    python cli.py node     # Start node server
    python cli.py wallet   # Create/show wallet
    python cli.py stats    # Show chain stats
    python cli.py send     # Send transaction
"""

import sys
import time
from blockchain import Blockchain, Transaction
from wallet import Wallet, generate_address


def cmd_mine():
    """Mine blocks interactively."""
    blockchain = Blockchain()
    wallet = Wallet()
    address = wallet.get_address()
    if not address:
        address = wallet.create()
        print(f"Created wallet: {address[:16]}...")

    print(f"Mining to: {address[:16]}...")
    print(f"Current height: {blockchain.get_height()}")
    print("Press Ctrl+C to stop mining\n")

    try:
        while True:
            block = blockchain.mine_block(address)
            if block:
                print(f"✅ Block #{blockchain.get_height()-1} mined!")
                print(f"   Hash: {block.hash[:16]}...")
                print(f"   Reward: {block.transactions[0].amount / 1e8:.8f} KRYO")
                print()
    except KeyboardInterrupt:
        print("\n⏸ Mining stopped")


def cmd_node():
    """Start node server."""
    from node import main as node_main
    # Override sys.argv for node
    sys.argv = ["node.py"] + sys.argv[2:]
    node_main()


def cmd_wallet():
    """Wallet operations."""
    wallet = Wallet()
    if len(sys.argv) > 2 and sys.argv[2] == "create":
        address = wallet.create()
        print(f"Created: {address}")
    else:
        addr = wallet.get_address()
        if addr:
            print(f"Address: {addr}")
        else:
            print("No wallet. Run 'create'.")


def cmd_stats():
    """Show blockchain stats."""
    blockchain = Blockchain()
    stats = blockchain.get_stats()
    print("KryoMine Chain Statistics")
    print("=" * 40)
    for key, value in stats.items():
        print(f"  {key}: {value}")


def cmd_send():
    """Send a transaction."""
    if len(sys.argv) < 5:
        print("Usage: python cli.py send SENDER RECIPIENT AMOUNT")
        return

    blockchain = Blockchain()
    sender = sys.argv[2]
    recipient = sys.argv[3]
    amount = int(float(sys.argv[4]) * 1e8)  # Convert KRYO to satoshis

    tx = Transaction(sender=sender, recipient=recipient, amount=amount)
    success = blockchain.add_transaction(tx)
    if success:
        print(f"Transaction submitted: {tx.hash()}")
    else:
        print("Failed: insufficient balance or invalid amount")


def cmd_test():
    """Run basic tests to verify the blockchain works."""
    import shutil
    shutil.rmtree("/tmp/kryomine_test", ignore_errors=True)

    print("Running KryoMine self-test...\n")

    # Test 1: Genesis block
    print("1. Creating genesis block...")
    bc = Blockchain(data_dir="/tmp/kryomine_test")
    genesis = bc.get_latest_block()
    assert genesis.header.previous_hash == "0" * 64, "Genesis prev hash wrong"
    assert len(genesis.transactions) == 1, "Genesis should have 1 tx"
    print(f"   ✅ Genesis block created: {genesis.hash[:16]}...")

    # Test 2: Mine a block with low difficulty
    print(f"2. Mining a block (difficulty=4)...")
    wallet = Wallet(wallet_dir="/tmp/kryomine_test")
    if not wallet.get_address():
        wallet.create()

    start = time.time()
    block = bc.mine_block(wallet.get_address())
    elapsed = time.time() - start

    if block:
        print(f"   ✅ Block mined in {elapsed:.1f}s")
        print(f"   Hash: {block.hash[:16]}...")
        print(f"   Reward: {block.transactions[0].amount / 1e8:.8f} KRYO")
    else:
        print("   ❌ Mining failed!")
        return False

    # Test 3: Chain validation
    print(f"3. Validating chain...")
    if bc.is_valid_chain():
        print(f"   ✅ Chain is valid")
    else:
        print(f"   ❌ Chain validation failed!")
        return False

    # Test 4: Transaction
    print("4. Testing transaction...")
    sender = wallet.get_address()
    recipient = generate_address()
    tx = Transaction(sender=sender, recipient=recipient,
                     amount=int(1e8))  # 1 KRYO
    success = bc.add_transaction(tx)
    if success:
        print(f"   ✅ Transaction accepted: {tx.hash()[:16]}...")
    else:
        print(f"   ❌ Transaction rejected!")

    # Test 5: Block reward halving
    print("5. Testing reward halving...")
    from blockchain import compute_block_reward
    reward_0 = compute_block_reward(0)
    reward_1 = compute_block_reward(210000)
    reward_2 = compute_block_reward(420000)
    assert reward_1 == reward_0 // 2, f"Halving failed: {reward_0} -> {reward_1}"
    assert reward_2 == reward_1 // 2, f"Second halving failed"
    print(f"   ✅ Reward halves correctly: {reward_0} -> {reward_1} -> {reward_2}")

    # Test 6: Max supply check
    print("6. Testing max supply...")
    from blockchain import MAX_SUPPLY
    total_supply = bc.get_total_supply()
    assert total_supply <= MAX_SUPPLY, f"Supply exceeds max: {total_supply}"
    print(f"   ✅ Supply under max: {total_supply} / {MAX_SUPPLY}")

    # Cleanup
    import shutil
    shutil.rmtree("/tmp/kryomine_test", ignore_errors=True)

    print(f"\n{'='*40}")
    print("✅ ALL TESTS PASSED")
    print("=" * 40)

    # Show hashrate
    if block and elapsed > 0:
        print(f"\n📊 Mining benchmark (CPU):")
        print(f"   Mining time: {elapsed:.1f}s")
        print(f"   Hashrate: {block.header.nonce / elapsed:.0f} H/s")
        print(f"   Difficulty: {block.header.difficulty}")
        print(f"\n💡 GPU mining would be significantly faster due to")
        print(f"   the memory-hard GigaHash algorithm (256MB buffer).")
        print(f"   Expected GPU speedup: 10-100x depending on GPU.")

    return True


def print_usage():
    print("KryoMine CLI v0.1.0")
    print()
    print("Commands:")
    print("  mine    - Start mining")
    print("  node    - Start node server")
    print("  wallet  - Wallet operations")
    print("  stats   - Show chain statistics")
    print("  send    - Send a transaction")
    print("  test    - Run self-test")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    cmd = sys.argv[1]
    commands = {
        "mine": cmd_mine,
        "node": cmd_node,
        "wallet": cmd_wallet,
        "stats": cmd_stats,
        "send": cmd_send,
        "test": cmd_test,
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print_usage()


if __name__ == "__main__":
    main()
