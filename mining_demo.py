import time
from blockchain import Block

if __name__ == "__main__":
    print(f"{'difficulty':>10} {'nonce':>10} {'time (s)':>10} hash")

    for difficulty in range(1, 6):
        block = Block(1, ["Alice pays Bob 5"], "0" * 64, timestamp=0)
        start = time.time()
        block.mine(difficulty)
        elapsed = time.time() - start

        print(f"{difficulty:>10} {block.nonce:>10} {elapsed:>10.3f} {block.hash[:24]}...")